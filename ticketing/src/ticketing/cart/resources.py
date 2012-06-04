# -*- coding:utf-8 -*-
import itertools
import operator
from sqlalchemy import sql
from pyramid.decorator import reify
from ticketing.products import models as p_models
from ticketing.venues import models as v_models
from . import security
from . import models as m

from . import logger

class TicketingCartResrouce(object):
    def __init__(self, request):
        self.request = request

    def _convert_order_product_items(self, ordered_products):
        """ 選択したProductからProductItemと個数の組に展開する
        :param ordered_products: list of (product, quantity)
        :return: iter of (product_item_id, quantity)
        """
        for product, quantity in ordered_products:
            for product_item in product.items:
                yield (product_item, quantity)

    def quantity_for_stock_id(self, ordered_products):
        """ ProductItemと個数の組から、stock_id, 個数の組に集約する
        :param ordered_product_items: iter of (product_item, quantity)

        """

        ordered_product_items = self._convert_order_product_items(ordered_products=ordered_products)
        q = sorted(ordered_product_items, key=lambda x: x[0].stock_id)
        q = itertools.groupby(q, key=lambda x: x[0].stock_id)
        return ((stock_id, sum(quantity for _, quantity in ordered_items)) for stock_id, ordered_items in q)



    def order_products(self, ordered_products):
        """

        プロダクトと数量の組を受け取る
        プロダクトアイテムと数量の組に変換
        同じ在庫にひもづくプロダクトアイテムを集約して在庫と数量の組に変換


        :param ordered_products: list of tuple(product, quantity)
        :returns: :class:`.models.Cart`
        """

        seat_statuses = []
        m.DBSession.bind.echo = True
        conn = m.DBSession.bind.connect()
        try:
            trans = conn.begin()
            # 在庫数確認、確保
            stock_quantity = list(self.quantity_for_stock_id(ordered_products))
            for stock_id, quantity in stock_quantity:
                # 必要数のある在庫を確保しながら確認
                up = p_models.StockStatus.__table__.update().values(
                        {"quantity": p_models.StockStatus.quantity - quantity}
                ).where(
                    sql.and_(p_models.StockStatus.stock_id==stock_id,
                             p_models.StockStatus.quantity >= quantity)
                )
                affected = conn.execute(up).rowcount
                if not affected:
                    trans.rollback() # 確保失敗 ロールバックして戻り
                    return
            trans.commit()
            trans = conn.begin()
            # 座席割当
            # 必要な席種かつ確保されていない座席
            # を含む必要数量の連席情報の最初の行
            for stock_id, quantity in stock_quantity:
                sub = sql.select([v_models.SeatAdjacency.id]).where(
                    sql.and_(
                        #確保されていない
                        v_models.SeatStatus.status == int(v_models.SeatStatusEnum.Vacant),
                        #必要な席種
                        p_models.Stock.id == stock_id,
                        p_models.Stock.id == v_models.Seat.stock_id,
                        v_models.SeatStatus.seat_id == v_models.Seat.id,
                        #必要数量の連席情報
                        v_models.SeatAdjacencySet.seat_count == quantity,
                        # 連席情報内の席割当
                        v_models.SeatAdjacencySet.id==v_models.SeatAdjacency.adjacency_set_id,
                        # 連席情報と席の紐付け
                        v_models.SeatAdjacency.id==v_models.seat_seat_adjacency_table.c.seat_adjacency_id,
                        v_models.Seat.id==v_models.seat_seat_adjacency_table.c.seat_id,
                    )
                ).limit(1)
                adjacency = conn.execute(sub).fetchone()
                if not adjacency:
                    trans.rollback() # 確保失敗 ロールバックして戻り
                    for stock_id, quantity in stock_quantity:
                        up = p_models.StockStatus.__table__.update().values(
                                {"quantity": p_models.StockStatus.quantity + quantity}
                        ).where(p_models.StockStatus.stock_id==stock_id)
                        affected = conn.execute(up).rowcount
                    return

                select = sql.select([v_models.SeatStatus.seat_id], for_update=True).where(
                    sql.and_(
                        #確保されていない
                        v_models.SeatStatus.status == int(v_models.SeatStatusEnum.Vacant),
                        v_models.SeatAdjacency.id==v_models.seat_seat_adjacency_table.c.seat_adjacency_id,
                        v_models.Seat.id==v_models.seat_seat_adjacency_table.c.seat_id,
                        v_models.SeatStatus.seat_id == v_models.Seat.id,
                        v_models.SeatAdjacency.id==adjacency[0],
                    )

                )
                seat_statuses = [s.seat_id for s in conn.execute(select)]

                if not seat_statuses:
                    trans.rollback() # 確保失敗 ロールバックして戻り
                    for stock_id, quantity in stock_quantity:
                        up = p_models.StockStatus.__table__.update().values(
                                {"quantity": p_models.StockStatus.quantity + quantity}
                        ).where(p_models.StockStatus.stock_id==stock_id)
                        affected = conn.execute(up).rowcount
                    return

                up = v_models.SeatStatus.__table__.update().values({
                    v_models.SeatStatus.status : int(v_models.SeatStatusEnum.InCart)
                }).where(
                    sql.and_(
                        v_models.SeatStatus.status == int(v_models.SeatStatusEnum.Vacant),
                        v_models.SeatStatus.seat_id.in_(seat_statuses)
                    )
                )
                affected = conn.execute(up).rowcount
                if affected != quantity:
                    logger.debug("require %d but affected %d" % (quantity, affected))
                    trans.rollback() # 確保失敗 ロールバックして戻り
                    for stock_id, quantity in stock_quantity:
                        up = p_models.StockStatus.__table__.update().values(
                                {"quantity": p_models.StockStatus.quantity + quantity}
                        ).where(p_models.StockStatus.stock_id==stock_id)
                        affected = conn.execute(up).rowcount
                    return


            trans.commit()
            trans = conn.begin()
            # カート作成
            # 注文明細作成
            #m.DBSession.remove() #ここから通常のORMセッション
            cart = m.Cart()
            if seat_statuses:
                seats = m.DBSession.query(v_models.Seat).filter(v_models.Seat.id.in_(seat_statuses)).all()
                cart.add_seat(seats, ordered_products)
            m.DBSession.add(cart)
            m.DBSession.flush()
            trans.commit()
            logger.info("cart created id = %d" % cart.id)
            return cart
        finally:
            conn.close()