# -*- coding:utf-8 -*-

"""

TODO: 引き当て処理自体はResourceから分離する。
TODO: cart取得
"""
import logging

from datetime import datetime, date
import itertools
from sqlalchemy import sql
from pyramid.security import Everyone, Authenticated
from pyramid.security import Allow
from pyramid.decorator import reify
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import joinedload
from zope.interface import implementer
from .interfaces import ICartPayment, ICartDelivery
from ticketing.payments.interfaces import IOrderPayment, IOrderDelivery 
from ticketing.mails.interfaces import ICompleteMailPayment, ICompleteMailDelivery, IOrderCancelMailPayment, IOrderCancelMailDelivery
from ticketing.mails.resources import CompleteMailPayment, CompleteMailDelivery, OrderCancelMailPayment, OrderCancelMailDelivery

from .exceptions import (
    OutTermSalesException,
    NoPerformanceError,
)
from ..core import models as c_models
from ..core import api as core_api
from ..users import models as u_models
from . import models as m
from . import logger
from zope.deprecation import deprecate

logger = logging.getLogger(__name__)

class TicketingCartResource(object):
    __acl__ = [
        (Allow, Authenticated, 'view'),
    ]

    def __init__(self, request):
        self.request = request
        self._event_id = None
        self._event = None
        if request.matchdict:
            self.event_id = self.request.matchdict.get('event_id')
        else:
            self.event_id = None

    def _get_event_id(self):
        return self._event_id

    def _set_event_id(self, value):
        self._event_id = value
        self._event = None

    event_id = property(_get_event_id, _set_event_id)

    # @property
    # def memberships(self):
    #     membergroups = self.membergroups
    #     if not membergroups:
    #         return []
    #     return [m.membership for m in membergroups]
    @property
    def memberships(self):
        organization = core_api.get_organization(self.request)
        logger.debug('organization %s' % organization.code)
        logger.debug('memberships %s' % organization.memberships)
        return organization.memberships

    # @property
    # def membergroup(self):
    #     sales_segment = self.sales_segment
    #     if sales_segment is None:
    #         return None
    #     return sales_segment.membergroup

    @property
    def event(self):
        if self._event is None:
            # TODO: ドメインで許可されるeventのみを使う
            organization = core_api.get_organization(self.request)
            try:
                self._event = c_models.Event.filter(c_models.Event.id==self.event_id).filter(c_models.Event.organization==organization).one()
            except NoResultFound:
                self._event = None
        return self._event


    @property
    def performance(self):
        performance_id = self.request.matchdict['performance_id']
        try:
            return c_models.Performance.query.filter_by(id=performance_id).one()
        except NoResultFound:
            raise NoPerformanceError




    @property
    def membergroups(self):
        sales_segment = self.sales_segment
        if sales_segment is None:
            return []
        return sales_segment.membergroups
        


    def get_system_fee(self):
        # 暫定で0に設定
        return 0

    @property
    def sales_counter_sales_segment(self):
        """ 当日用販売区分"""
        # FIXME: kind を見る運用でいいのかしら?
        # SalesSegmentGroup にフラグを持たせる方がよいかも?
        scs = [s for s in self.sales_segments if s.sales_segment_group.kind == 'sales_counter']
        if not scs:
            return None
        return scs[0]

    @property
    def normal_sales_segment(self):
        """ 当日以外販売区分"""
        scs = [s for s in self.sales_segments if s.sales_segment_group.kind != 'sales_counter']
        if not scs:
            return None
        return scs[0]

    def get_payment_delivery_method_pair(self, start_on=None):
        segment = self.get_sales_segment()
        q = c_models.PaymentDeliveryMethodPair.query.filter(
            c_models.PaymentDeliveryMethodPair.sales_segment_group_id==segment.id
        ).filter(
            c_models.PaymentDeliveryMethodPair.public==1,
        ).order_by(
            c_models.PaymentDeliveryMethodPair.transaction_fee,
            c_models.PaymentDeliveryMethodPair.payment_method_id,
            c_models.PaymentDeliveryMethodPair.delivery_fee,
            c_models.PaymentDeliveryMethodPair.delivery_method_id,
        )
        if start_on:
            today = date.today()
            period_days = date(start_on.year, start_on.month, start_on.day) - today
            q = q.filter(
                c_models.PaymentDeliveryMethodPair.unavailable_period_days<=period_days.days
            )
        pairs = q.all()
        return pairs

    def authenticated_user(self):
        from ticketing.rakuten_auth.api import authenticated_user
        user = authenticated_user(self.request)
        return user


    @deprecate("deprecated method")
    def get_sales_segument(self):
        return self.get_sales_segment()

    @property
    def sales_segments(self):
        """ イベントに関連する全販売区分 """
        now = datetime.now()
        q = c_models.SalesSegment.query
        q = q.filter(c_models.SalesSegment.public==1)
        q = q.filter(c_models.SalesSegmentGroup.public==1)
        q = q.filter(c_models.SalesSegmentGroup.event_id==self.event_id)
        q = q.filter(c_models.SalesSegment.sales_segment_group_id==c_models.SalesSegmentGroup.id)
        q = q.filter(
            c_models.SalesSegment.start_at <= now
        ).filter(
            c_models.SalesSegment.end_at >= now
        )
        user = self.authenticated_user()
        if user and user.get('is_guest'):
            q = q.filter(
                c_models.SalesSegment.id==u_models.MemberGroup_SalesSegment.c.sales_segment_group_id
            ).filter(
                u_models.MemberGroup_SalesSegment.c.membergroup_id==u_models.MemberGroup.id
            ).filter(
                u_models.MemberGroup.is_guest==True
            )

        elif user and 'membership' in user:
            q = q.filter(
                c_models.SalesSegment.id==u_models.MemberGroup_SalesSegment.c.sales_segment_group_id
            ).filter(
                u_models.MemberGroup_SalesSegment.c.membergroup_id==u_models.MemberGroup.id
            ).filter(
                u_models.MemberGroup.name==user['membergroup']
            )
        sales_segments = q.all()
        return sales_segments

    @deprecate('use get_next_and_last_sales_segment_period')
    def get_next_sales_segment(self):
        """ 該当イベントの次回SalesSegment取得
        """
        return self.event.query_next_sales_segments(user=self.authenticated_user()).order_by('SalesSegment.start_at').first()

    def get_next_and_last_sales_segment_period(self):
        return self.event.get_next_and_last_sales_segment_period(user=self.authenticated_user())

    def get_sales_segment(self):
        """ 該当イベントのSalesSegment取得
        """

        if not getattr(self.request, 'matchdict'):
            return None
        sales_segment_group_id = self.request.matchdict.get('sales_segment_id')
        if sales_segment_group_id is None:
            return None

        now = datetime.now()
        q = c_models.SalesSegment.query
        q = q.filter(c_models.SalesSegmentGroup.public==1)
        q = q.filter(c_models.SalesSegment.public==1)
        if self.event_id:
            q = q.filter(c_models.SalesSegment.event_id==self.event_id)

        q = q.filter(
            c_models.SalesSegment.id==sales_segment_group_id
        )

        user = self.authenticated_user()
        if user and user.get('is_guest'):
            q = q.filter(
                c_models.SalesSegment.id==u_models.MemberGroup_SalesSegment.c.sales_segment_group_id
            ).filter(
                u_models.MemberGroup_SalesSegment.c.membergroup_id==u_models.MemberGroup.id
            ).filter(
                u_models.MemberGroup.is_guest==True
            )

        elif user and 'membership' in user:
            q = q.filter(
                c_models.SalesSegment.id==u_models.MemberGroup_SalesSegment.c.sales_segment_group_id
            ).filter(
                u_models.MemberGroup_SalesSegment.c.membergroup_id==u_models.MemberGroup.id
            ).filter(
                u_models.MemberGroup.name==user['membergroup']
            )

        sales_segment = q.first()
        if sales_segment is None:
            return None

        if sales_segment.start_at >= now or sales_segment.end_at <= now:
            next = self.context.get_next_sales_segment_period()
            if next:
                raise OutTermSalesException(
                    event=next['performance'].event,
                    **next)
            else:
                raise HTTPNotFound()

        return sales_segment

    sales_segment = property(get_sales_segment)

    @deprecate("deprecated method")
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

    @deprecate("deprecated method")
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


    @deprecate("deprecated method")
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

    @deprecate("deprecated method")
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
                    c_models.SeatAdjacency.id==c_models.Seat_SeatAdjacency.seat_adjacency_id,
                    c_models.Seat.id==c_models.Seat_SeatAdjacency.seat_id,
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
                    c_models.SeatAdjacency.id==c_models.Seat_SeatAdjacency.seat_adjacency_id,
                    c_models.Seat.id==c_models.Seat_SeatAdjacency.seat_id,
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
                    c_models.SeatAdjacency.id==c_models.Seat_SeatAdjacency.seat_adjacency_id,
                    c_models.Seat.id==c_models.Seat_SeatAdjacency.seat_id,
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

    def _create_cart(self, seat_statuses, ordered_products, performance_id):
        cart = m.Cart.create(system_fee=self.get_system_fee())
        seats = m.DBSession.query(c_models.Seat).filter(c_models.Seat.id.in_(seat_statuses)).all()
        cart.add_seat(seats, ordered_products)
        m.DBSession.add(cart)
        m.DBSession.flush()
        return cart

    def _create_cart_with_quantity(self, stock_quantity, ordered_products, performance_id):
        cart = m.Cart.create(performance_id=performance_id, system_fee=self.get_system_fee())
        cart.add_products(ordered_products)
        m.DBSession.add(cart)
        m.DBSession.flush()
        return cart

    # TODO: それぞれのテストパターンを増やす
    # 問題となったパターン (暫定対応の条件追加済)
    # パフォーマンスがことなるプロダクトアイテムまで参照しにいってしまう
    # 確保済みシートを含むadjacencyを参照してしまう
    @deprecate("deprecated method")
    def order_products(self, performance_id, ordered_products):
        """

        プロダクトと数量の組を受け取る
        プロダクトアイテムと数量の組に変換
        同じ在庫にひもづくプロダクトアイテムを集約して在庫と数量の組に変換


        :param ordered_products: list of tuple(product, quantity)
        :returns: :class:`.models.Cart`
        """

        performance_id = int(performance_id)
        logger.debug("order performance_id = %s, ordered_products = %s" % (performance_id, ordered_products))
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
                cart = self._create_cart(seat_statuses, ordered_products, performance_id)
            else:
                # 数受けの場合は数量を渡す
                cart = self._create_cart_with_quantity(stock_quantity, ordered_products, performance_id)

            trans.commit()
            logger.info("cart created id = %d" % cart.id)
            return cart
        finally:
            conn.close()

    @property
    def membership(self):
        from ticketing.rakuten_auth.api import authenticated_user
        user = authenticated_user(self.request)
        if user is None:
            return None
        if 'membership' not in user:
            return None

        membership = user['membership']
        return membership

    # TODO: users.api に移動
    def get_or_create_user(self):
        # TODO: 依存関係がおかしいので確認 なぜrakuten_authがcart.apiを使うのか？
        from ticketing.rakuten_auth.api import authenticated_user
        from . import api
        openid = authenticated_user(self.request)
        if openid is None or openid.get('is_guest', False):
            return None

        if 'clamed_id' in openid:
            auth_identifier = openid['clamed_id']
            membership = 'rakuten'
        elif 'username' in openid:
            auth_identifier = openid['username']
            membership = openid['membership']
        user = api.get_or_create_user(self.request, auth_identifier, membership)
        return user

    @reify
    def host_base_url(self):
        return core_api.get_host_base_url(self.request)

@implementer(IOrderDelivery)
class OrderDelivery(object):
    def __init__(self, order):
        self.order = order

@implementer(ICartDelivery)
class CartDelivery(object):
    def __init__(self, cart):
        self.cart = cart

@implementer(IOrderPayment)
class OrderPayment(object):
    def __init__(self, order):
        self.order = order

@implementer(ICartPayment)
class CartPayment(object):
    def __init__(self, cart):
        self.cart = cart
