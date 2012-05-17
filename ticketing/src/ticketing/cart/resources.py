# -*- coding:utf-8 -*-
import itertools
import operator
from sqlalchemy import sql
from pyramid.decorator import reify
from ticketing.products import models as p_models
from ticketing.venues import models as v_models
from . import security
from . import models as m

class TicketingCartResrouce(object):
    def __init__(self, request):
        self.request = request

    def acquire_product(self, product, amount):
        """ 商品確保
        """

        for product_item in product.items:
            self.acquire_product_item(product_item, amount)

    def get_stock_status(self, product_item_id):
        """
        ProductItem -> Stock -> StockStatus
        :param product_item_id: プロダクトアイテムID
        :return: :class:`ticketing.products.models.StockStatus`
        """
        return m.DBSession.query(p_models.StockStatus).filter(
                p_models.ProductItem.id==product_item_id
            ).filter(
                p_models.ProductItem.stock_id==p_models.Stock.id
            ).filter(
                p_models.Stock.id==p_models.StockStatus.stock_id
            ).one()

    def has_stock(self, product_item_id, quantity):
        """在庫確認(Stock)
        :param product_item_id:
        :param quantity: 要求数量
        :return: bool
        """
        stock_status = self.get_stock_status(product_item_id=product_item_id)
        return stock_status.quantity >= quantity

    def acquire_product_item(self, product_item, amount):
        # 在庫チェック
        if not self.has_stock(amount, product_item):
            raise Exception # TODO: 例外クラス定義

        self.cart.add_product_item(product_item, amount)

    @reify
    def cart_session_id(self):
        return security.cart_session_id(self.request)

    @reify
    def cart(self):
        return m.Cart.get_or_create(self.cart_session_id)

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


    def select_seat(self, stock_id, quantity):
        """ 指定在庫（席種）を隣接座席で確保する
        必要な席種かつ確保されていない座席
        を含む必要数量の連席情報の最初の行

        :param stock_id: 在庫ID
        :param quantity: 数量
        :return: list of :class:`ticketing.venues.models.SeatStatus`
        """

        sub = m.DBSession.query(v_models.SeatAdjacencySet.id).filter(
                # 確保されていない
                v_models.SeatStatus.status==int(v_models.SeatStatusEnum.Vacant)
            ).filter(
                # 確保されてない状態と席の紐付け
                v_models.SeatStatus.seat_id==v_models.Seat.id
            ).filter(
                # 席と在庫の紐付け
                p_models.Stock.id==v_models.Seat.stock_id
            ).filter(
                # 対象とする在庫(席種)
                p_models.Stock.id==stock_id
            ).filter(
                # 必要数量の連席情報
                v_models.SeatAdjacencySet.seat_count==quantity
            ).filter(
                # 連席情報内の席割当
                v_models.SeatAdjacencySet.id==v_models.SeatAdjacency.adjacency_set_id
            ).filter(
                # 連席情報と席の紐付け
                v_models.SeatAdjacency.id==v_models.seat_seat_adjacency_table.c.seat_adjacency_id
            ).filter(
                v_models.Seat.id==v_models.seat_seat_adjacency_table.c.seat_id
            ).limit(1)


        seat_statuses = m.DBSession.query(v_models.SeatStatus).filter(
                v_models.SeatStatus.seat_id==v_models.Seat.id
            ).filter(
                v_models.Seat.id==v_models.seat_seat_adjacency_table.c.seat_id
            ).filter(
                v_models.SeatAdjacency.id==v_models.seat_seat_adjacency_table.c.seat_adjacency_id
            ).filter(
                v_models.SeatAdjacency.adjacency_set_id.in_(sub)
            ).all()

        if len(seat_statuses) == quantity:
            up = sql.update(v_models.SeatStatus.__table__).values({v_models.SeatStatus.status: int(v_models.SeatStatusEnum.InCart)}).where(v_models.SeatStatus.seat_id.in_([s.seat_id for s in seat_statuses]))
            m.DBSession.bind.execute(up)

        return seat_statuses

    def order(self, ordered_products):
        """

        プロダクトと数量の組を受け取る
        プロダクトアイテムと数量の組に変換
        同じ在庫にひもづくプロダクトアイテムを集約して在庫と数量の組に変換


        :param ordered_products: list of tuple(product, quantity)
        :returns: :class:`.models.Cart`
        """

        # SeatとProductItemとどちらで処理を進めるか検討 座席割当はSeatでないといけない
        seats = []
        cart = m.Cart()
        # このループはSeatTypeであるべき
        for stock_id, quantity in self.quantity_for_stock_id(ordered_products):
            if not self.has_stock(stock_id, quantity):
                return False
            seats += self.select_seat(stock_id, quantity)
        # TODO: Cart作成,CartedProductItemに座席割当(Cart,CartedProduct, CartedProductItem)
        cart.add_seat(seats)