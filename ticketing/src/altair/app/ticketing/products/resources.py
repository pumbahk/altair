# -*- coding: utf-8 -*-
import json
import logging
from altair.sqlahelper import get_db_session
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPNotFound, HTTPBadRequest
from sqlalchemy.orm.exc import NoResultFound

from altair.app.ticketing.resources import TicketingAdminResource
from altair.app.ticketing.core.models import Product, ProductItem, SalesSegment, Organization, StockType
from altair.app.ticketing.orders.models import Order, OrderedProductItemToken
from altair.app.ticketing.payments.plugins import SEJ_DELIVERY_PLUGIN_ID, FAMIPORT_DELIVERY_PLUGIN_ID
from altair.app.ticketing.orders.models import ExternalSerialCodeProductItemPair, ExternalSerialCode
logger = logging.getLogger(__name__)


class ExternalSerialCodeResourceMixin(object):

    def __init__(self, request):
        super(ExternalSerialCodeResourceMixin, self).__init__(request)
        self.session = get_db_session(request, 'slave')

    def validate_setting_id(self):
        # 存在していなかったらNG
        code = self.session.query(ExternalSerialCode).filter(
            ExternalSerialCode.external_serial_code_setting_id == self.setting_id).first()
        if code:
            return True
        return False

    def save_setting_id(self, product_item_id, setting_id):
        pair = ExternalSerialCodeProductItemPair.query.filter(
            ExternalSerialCodeProductItemPair.product_item_id == product_item_id).first()
        if not pair:
            pair = ExternalSerialCodeProductItemPair()
        pair.product_item_id = product_item_id
        pair.external_serial_code_setting_id = setting_id
        pair.save()


class ProductResource(TicketingAdminResource):

    def __init__(self, request):
        super(ProductResource, self).__init__(request)
        self.product_id = None
        self.product_item_id = None

        if not self.user:
            return

        try:
            self.product_id = long(self.request.matchdict.get('product_id'))
        except (TypeError, ValueError):
            raise HTTPNotFound()

        try:
            self.product_item_id = long(self.request.params.get('product_item_id'))
        except (TypeError, ValueError):
            pass

    @reify
    def product(self):
        try:
            p = Product.query.join(SalesSegment).filter(
                    Product.id==self.product_id,
                    SalesSegment.organization_id==self.user.organization_id
                    ).one()
        except NoResultFound:
            raise HTTPNotFound()
        return p

    @reify
    def product_item(self):
        p = None
        if self.product_item_id is not None:
            try:
                p = ProductItem.query.join(ProductItem.product, Product.sales_segment).filter(
                        ProductItem.id==self.product_item_id,
                        SalesSegment.organization_id==self.user.organization_id
                        ).one()
            except NoResultFound:
                raise HTTPNotFound()
        return p


class ProductAPIResource(TicketingAdminResource):
    def __init__(self, request):
        super(ProductAPIResource, self).__init__(request)
        self.sales_segment_id = None

        if not self.user:
            return

        try:
            self.sales_segment_id = long(self.request.params.get('sales_segment_id'))
        except (TypeError, ValueError):
            raise HTTPNotFound()

    @reify
    def sales_segment(self):
        try:
            s = SalesSegment.query.join(Organization).filter(
                    SalesSegment.id==self.sales_segment_id,
                    Organization.id==self.user.organization_id
                    ).one()
        except NoResultFound:
            raise HTTPBadRequest(body=json.dumps(dict(message=u'販売区分が存在しません')))
        return s


class ProductShowResource(TicketingAdminResource):
    def __init__(self, request):
        super(ProductShowResource, self).__init__(request)
        self.sales_segment_id = None

        if not self.user:
            return

        try:
            self.sales_segment_id = long(self.request.matchdict.get('sales_segment_id'))
        except (TypeError, ValueError):
            raise HTTPNotFound()

    @reify
    def sales_segment(self):
        try:
            s = SalesSegment.query.join(Organization).filter(
                    SalesSegment.id==self.sales_segment_id,
                    Organization.id==self.user.organization_id
                    ).one()
        except NoResultFound:
            raise HTTPNotFound()
        return s


class ProductItemResource(TicketingAdminResource):

    def __init__(self, request):
        super(ProductItemResource, self).__init__(request)
        self.product_item_id = None

        if not self.user:
            return

        try:
            self.product_item_id = long(self.request.matchdict.get('product_item_id'))
        except (TypeError, ValueError):
            raise HTTPNotFound()

    @reify
    def product_item(self):
        try:
            p = ProductItem.query.join(ProductItem.product, Product.sales_segment).filter(
                    ProductItem.id==self.product_item_id,
                    SalesSegment.organization_id==self.user.organization_id
                    ).one()
        except NoResultFound:
            raise HTTPNotFound()
        return p


class ProductCreateResource(TicketingAdminResource, ExternalSerialCodeResourceMixin):

    def __init__(self, request):
        super(ProductCreateResource, self).__init__(request)
        self.sales_segment_id = None

        if not self.user:
            return

        try:
            self.sales_segment_id = long(self.request.params.get('sales_segment_id'))
        except (TypeError, ValueError):
            pass

    @reify
    def sales_segment(self):
        s = None
        if self.sales_segment_id is not None:
            try:
                s = SalesSegment.query.join(Organization).filter(
                        SalesSegment.id==self.sales_segment_id,
                        Organization.id==self.user.organization_id
                        ).one()
            except NoResultFound:
                raise HTTPNotFound()
        return s

    @reify
    def copy_sales_segments(self):
        s = SalesSegment.query \
            .filter(SalesSegment.performance_id == self.sales_segment.performance_id) \
            .filter(SalesSegment.id != self.sales_segment.id).all()
        return s


csv_header = [
    ('barcode_no', u'バーコード番号'),
    ('order_no', u'整理番号'),
    ('branch_no', u'チケット枝番'),
    ('last_name', u'氏名姓'),
    ('first_name', u'氏名名'),
    ('tel', u'電話番号'),
    ('performance_date', u'公演日'),
    ('stock_type', u'席種'),
    ('seat_no', u'管理番号'),
    ('ticket_count', u'チケット枚数'),
    ('gate_name', u'ゲート名')
]


class TapirsProductResource(ProductResource):

    @staticmethod
    def get_stock_type_by_id(session, stock_type_id):
        return session.query(StockType) \
            .filter(StockType.id == stock_type_id) \
            .filter(StockType.deleted_at == None) \
            .one()

    @staticmethod
    def get_token_by_id(session, token_id):
        return session.query(OrderedProductItemToken) \
            .filter(OrderedProductItemToken.id == token_id) \
            .filter(OrderedProductItemToken.deleted_at == None) \
            .one()

    def get_tapirs_from_seven(self, order, session):
        sej_order = order.sej_order
        export_data_seven = list()
        for i, ticket in enumerate(sej_order.tickets):
            # Todo:barcode_noの重複チェック
            try:
                if not ticket.ordered_product_item_token:
                    logger.warn(
                        'SejTicket.barcode_number={} has no relation with token.'.format(ticket.barcode_number))
                    continue
                if not ticket.ordered_product_item_token.seat:
                    logger.warn(
                        'SejTicket.barcode_number={} is not seat selectable.'.format(ticket.barcode_number))
                    continue
                stock_type_id = ticket.ordered_product_item_token.seat.stock.stock_type_id
                stock_type = self.get_stock_type_by_id(session, stock_type_id)
            except NoResultFound:
                logger.warn(
                    'no result was found for StockType.id={}.(Order.order_no={}, SejTicket.id={})'.format(
                        stock_type_id, order.order_no, sej_order.id))
                continue

            retval = dict(
                barcode_no=ticket.barcode_number,
                order_no=order.order_no,
                branch_no=i + 1,
                last_name=order.shipping_address.last_name.encode('utf-8'),
                first_name=order.shipping_address.first_name.encode('utf-8'),
                tel=order.shipping_address.tel_1 or order.shipping_address.tel_2,
                performance_date=order.performance.start_on,
                stock_type=stock_type.name.encode('utf-8'),
                seat_no=ticket.ordered_product_item_token.seat.seat_no,
                ticket_count=len(sej_order.tickets),
                gate_name=None
            )
            logger.info('barcode_num={}, order_no={}, seat_no={}'.format(retval.get('barcode_no'),
                                                                         retval.get('order_no'),
                                                                         retval.get('seat_no')))
            export_data_seven.append(retval)
        return export_data_seven

    def get_tapirs_from_famiport(self, order, session):
        fm_order = order.famiport_order
        ticket_likes = fm_order.get('famiport_tickets')
        export_data_famiport = list()
        for i, ticket_like in enumerate(ticket_likes):
            try:
                if not ticket_like.get('userside_token_id'):
                    logger.warn('FamiPortTicket.barcode_number={} has no relation with token.'.format(
                        ticket_like.get('barcode_number')))
                    continue
                token = self.get_token_by_id(session, ticket_like.get('userside_token_id'))
                if not token.seat:
                    logger.warn('FamiPortTicket.barcode_number={} is not seat selectable.'.format(
                        ticket_like.get('barcode_number')))
                    continue
                stock_type_id = token.seat.stock.stock_type_id
                stock_type = self.get_stock_type_by_id(session, stock_type_id)
            except NoResultFound:
                logger.warn(
                    'no result was found for StockType.id={}.(Order.order_no={}, FamiPortTicket.id={})'.format(
                        stock_type_id, order.order_no, ticket_like.get('id')))
                continue

            # famiportのバーコード番号には固定値で1が付与される。バーコード印字のタイミングでFM側で付与するものなのでチケスタDB内では付与されていない。
            retval = dict(
                barcode_no='{0}{1}'.format('1', ticket_like.get('barcode_number')),
                order_no=order.order_no,
                branch_no=i + 1,
                last_name=order.shipping_address.last_name.encode('utf-8'),
                first_name=order.shipping_address.first_name.encode('utf-8'),
                tel=order.shipping_address.tel_1 or order.shipping_address.tel_2,
                performance_date=order.performance.start_on,
                stock_type=stock_type.name.encode('utf-8'),
                seat_no=token.seat.seat_no,
                ticket_count=len(ticket_likes),
                gate_name=None
            )
            logger.info('barcode_num={}, order_no={}, seat_no={}'.format(retval.get('barcode_no'),
                                                                         retval.get('order_no'),
                                                                         retval.get('seat_no')))
            export_data_famiport.append(retval)
        return export_data_famiport

    @staticmethod
    def create_tapirs_dict(export_data):
        keys = [k for k, v in csv_header]
        csv_data = list()
        for d in export_data:
            row = dict()
            for k in keys:
                if d[k] is None:
                    row[k] = u''
                else:
                    if isinstance(d[k], str):
                        row[k] = unicode(d[k], 'utf-8')
                    else:
                        row[k] = d[k]

            sorted_row = dict()
            for k, v in sorted(row.items()):
                sorted_row.update({k: v})
            csv_data.append(sorted_row)
        return csv_data

    def get_tapirs(self, sales_segment_id, product_id):
        session = get_db_session(self.request, 'slave')
        orders = session.query(Order)\
            .join(SalesSegment, Order.sales_segment_id == SalesSegment.id) \
            .join(Product, SalesSegment.id == Product.sales_segment_id) \
            .filter(Order.sales_segment_id == sales_segment_id) \
            .filter(Order.canceled_at == None) \
            .filter(Order.deleted_at == None) \
            .filter(Order.refunded_at == None) \
            .filter(Product.id == product_id) \
            .all()

        # orderからcsv出力するためのdictへ変換
        export_data = []
        for order in orders:
            # ordersからコンビニ発券なもののみ処理
            # sejの場合
            if order.delivery_plugin_id == SEJ_DELIVERY_PLUGIN_ID:
                retval = self.get_tapirs_from_seven(order, session)
                for ret in retval:
                    if ret:
                        export_data.append(ret)
            # famiportの場合
            elif order.delivery_plugin_id == FAMIPORT_DELIVERY_PLUGIN_ID:
                retval = self.get_tapirs_from_famiport(order, session)
                for ret in retval:
                    if ret:
                        export_data.append(ret)

        csv_data = self.create_tapirs_dict(export_data)
        return csv_data
