# -*- coding:utf-8 -*-
import itertools
import operator
from sqlalchemy import sql
from pyramid.decorator import reify
from ..core import models as c_models
from . import security
from . import models as m

from . import logger

class TicketingCartResrouce(object):
    def __init__(self, request):
        self.request = request

    def _convert_order_product_items(self, performance_id, ordered_products):
        """ 選択したProductからProductItemと個数の組に展開する
        :param ordered_products: list of (product, quantity)
        :return: iter of (product_item_id, quantity)
        """
        for product, quantity in ordered_products:
            for product_item in m.DBSession.query(c_models.ProductItem).filter(
                        c_models.ProductItem.product_id==product.id).filter(
                        c_models.ProductItem.performance_id==performance_id).all():
                yield (product_item, quantity)

    def quantity_for_stock_id(self, performance_id, ordered_products):
        """ ProductItemと個数の組から、stock_id, 個数の組に集約する
        :param ordered_product_items: iter of (product_item, quantity)

        """

        ordered_product_items = self._convert_order_product_items(performance_id, ordered_products=ordered_products)
        ordered_product_items = list(ordered_product_items)
        logger.debug("ordered product items: %s" % ordered_product_items)
        q = sorted(ordered_product_items, key=lambda x: x[0].stock_id)
        q = itertools.groupby(q, key=lambda x: x[0].stock_id)
        return ((stock_id, sum(quantity for _, quantity in ordered_items)) for stock_id, ordered_items in q)


    def _get_stock(self, conn, performance_id, ordered_products):
        """ 在庫確保
        """

        # 在庫数確認、確保
        stock_quantity = list(self.quantity_for_stock_id(performance_id, ordered_products))
        for stock_id, quantity in stock_quantity:
            if quantity == 0:
                continue

            # 必要数のある在庫を確保しながら確認
            up = c_models.StockStatus.__table__.update().values(
                    {"quantity": c_models.StockStatus.quantity - quantity}
            ).where(
                sql.and_(c_models.StockStatus.stock_id==stock_id,
                    c_models.StockStatus.quantity >= quantity)
            )
            affected = conn.execute(up).rowcount
            if not affected:
                return False
        return stock_quantity

    def _get_seats(self, conn, stock_quantity):
        """ 座席確保
        """
        seat_statuses = []

        # 座席割当
        # 必要な席種かつ確保されていない座席
        # を含む必要数量の連席情報の最初の行
        for stock_id, quantity in stock_quantity:
            if quantity == 0:
                continue
            no_vacants = sql.select([c_models.SeatAdjacency.id]).where(
                sql.and_(
                    c_models.SeatAdjacency.id==c_models.seat_seat_adjacency_table.c.seat_adjacency_id,
                    c_models.Seat.id==c_models.seat_seat_adjacency_table.c.seat_id,
                    c_models.SeatStatus.seat_id == c_models.Seat.id,
                    c_models.SeatStatus.status != int(c_models.SeatStatusEnum.Vacant),
                    c_models.SeatAdjacencySet.seat_count == quantity,
                    c_models.Stock.id == stock_id,
                    c_models.Stock.id == c_models.Seat.stock_id,
                ),
            )
            no_vacants = [r[0] for r in conn.execute(no_vacants)]
            sub = sql.select([c_models.SeatAdjacency.id]).where(
                sql.and_(
                    #確保されていない
                    c_models.SeatStatus.status == int(c_models.SeatStatusEnum.Vacant),
                    #必要な席種
                    c_models.Stock.id == stock_id,
                    c_models.Stock.id == c_models.Seat.stock_id,
                    c_models.SeatStatus.seat_id == c_models.Seat.id,
                    #必要数量の連席情報
                    c_models.SeatAdjacencySet.seat_count == quantity,
                    # 連席情報内の席割当
                    c_models.SeatAdjacencySet.id==c_models.SeatAdjacency.adjacency_set_id,
                    # 連席情報と席の紐付け
                    c_models.SeatAdjacency.id==c_models.seat_seat_adjacency_table.c.seat_adjacency_id,
                    c_models.Seat.id==c_models.seat_seat_adjacency_table.c.seat_id,
                    # 確保済みの席と紐づいていない
                    sql.not_(c_models.SeatAdjacency.id.in_(no_vacants)),
                )
            ).limit(1)
            adjacency = conn.execute(sub).fetchone()
            if not adjacency:
                return False

            select = sql.select([c_models.SeatStatus.seat_id], for_update=True).where(
                sql.and_(
                    #確保されていない
                    c_models.SeatStatus.status == int(c_models.SeatStatusEnum.Vacant),
                    c_models.SeatAdjacency.id==c_models.seat_seat_adjacency_table.c.seat_adjacency_id,
                    c_models.Seat.id==c_models.seat_seat_adjacency_table.c.seat_id,
                    c_models.SeatStatus.seat_id == c_models.Seat.id,
                    c_models.SeatAdjacency.id==adjacency[0],
                )

            )
            seat_statuses = [s.seat_id for s in conn.execute(select)]

            if not seat_statuses:
                return False

            up = c_models.SeatStatus.__table__.update().values({
                c_models.SeatStatus.status : int(c_models.SeatStatusEnum.InCart)
            }).where(
                sql.and_(
                    c_models.SeatStatus.status == int(c_models.SeatStatusEnum.Vacant),
                    c_models.SeatStatus.seat_id.in_(seat_statuses)
                )
            )
            affected = conn.execute(up).rowcount
            if affected != quantity:
                logger.debug("require %d but affected %d" % (quantity, affected))
                trans.rollback() # 確保失敗 ロールバックして戻り
                for stock_id, quantity in stock_quantity:
                    up = c_models.StockStatus.__table__.update().values(
                            {"quantity": c_models.StockStatus.quantity + quantity}
                    ).where(c_models.StockStatus.stock_id==stock_id)
                    affected = conn.execute(up).rowcount
                return

            return seat_statuses

    def _create_cart(self, seat_statuses, ordered_products):
        cart = m.Cart()
        seats = m.DBSession.query(c_models.Seat).filter(c_models.Seat.id.in_(seat_statuses)).all()
        cart.add_seat(seats, ordered_products)
        m.DBSession.add(cart)
        m.DBSession.flush()
        return cart

    def _create_cart_with_quantity(self, stock_quantity, ordered_products):
        cart = m.Cart()
        cart.add_products(ordered_products)
        m.DBSession.add(cart)
        m.DBSession.flush()
        return cart

    # TODO: それぞれのテストパターンを増やす
    # 問題となったパターン (暫定対応の条件追加済)
    # パフォーマンスがことなるプロダクトアイテムまで参照しにいってしまう
    # 確保済みシートを含むadjacencyを参照してしまう
    def order_products(self, performance_id, ordered_products):
        """

        プロダクトと数量の組を受け取る
        プロダクトアイテムと数量の組に変換
        同じ在庫にひもづくプロダクトアイテムを集約して在庫と数量の組に変換


        :param ordered_products: list of tuple(product, quantity)
        :returns: :class:`.models.Cart`
        """

        m.DBSession.bind.echo = True
        conn = m.DBSession.bind.connect()
        try:

            trans = conn.begin()
            stock_quantity = self._get_stock(conn, performance_id, ordered_products)
            if not stock_quantity:
                trans.rollback()
                return
            trans.commit()

            # TODO: 数受けの場合は座席確保しない
            seat_statuses = []
            if False:
                trans = conn.begin()
                seat_statuses = self._get_seats(conn, stock_quantity)
                if not seat_statuses:
                    trans.rollback() # 確保失敗 ロールバックして戻り
                    trans = conn.begin()
                    for stock_id, quantity in stock_quantity:
                        up = c_models.StockStatus.__table__.update().values(
                                {"quantity": c_models.StockStatus.quantity + quantity}
                        ).where(c_models.StockStatus.stock_id==stock_id)
                        affected = conn.execute(up).rowcount
                    trans.commit()
                    return
                trans.commit()


            trans = conn.begin()
            # TODO: ここでも例外処理で在庫戻しが必要
            cart = None
            if False: # QAのため数受け処理のみ
                cart = self._create_cart(seat_statuses, ordered_products)
            else:
                # 数受けの場合は数量を渡す
                cart = self._create_cart_with_quantity(stock_quantity, ordered_products)

            trans.commit()
            logger.info("cart created id = %d" % cart.id)
            return cart
        finally:
            conn.close()
