# -*- coding:utf-8 -*-
from datetime import datetime
import logging

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPBadRequest
from sqlalchemy.orm.exc import NoResultFound
from altair.mobile import mobile_view_config
from wtforms.validators import ValidationError
from ticketing.models import DBSession
from ticketing.core.models import PaymentDeliveryMethodPair, Performance, Product
from ticketing.cart import api as cart_api
from ticketing.cart.views import back
from ticketing.payments.payment import Payment
from ticketing.cart.exceptions import NoCartError

from . import api
from . import helpers as h
from . import schemas
from . import selectable_renderer
from .exceptions import NotElectedException
from .models import (
    LotEntry,
    LotEntryWish,
    LotElectedEntry,
)
from . import urls

logger = logging.getLogger(__name__)



@mobile_view_config(context=NoResultFound)
def no_results_found(context, request):
    """ 改良が必要。ログに該当のクエリを出したい。 """
    logger.warning(context)    
    return HTTPNotFound()

@mobile_view_config(context=NoCartError)
def no_cart_error(context, request):
    logger.warning(context)
    return HTTPNotFound()


def back_to_step1(request):
    context = request.context
    return HTTPFound(request.route_path('lots.entry.step1', event_id=context.event.id, lot_id=context.lot.id, option_index=context.option_index))

def back_to_step3(request):
    context = request.context
    return HTTPFound(request.route_path('lots.entry.step3', event_id=context.event.id, lot_id=context.lot.id))

@view_defaults(request_type='altair.mobile.interfaces.IMobileRequest')
class EntryLotView(object):
    """
    申し込み画面
    商品 x 枚数 を入力
    購入者情報を入力
    決済方法を選択
    """

    def __init__(self, context, request):
        self.request = request
        self.context = context

    @view_config(route_name='lots.entry.index', renderer=selectable_renderer("mobile/%(membership)s/index.html"))
    def index(self):
        event = self.context.event
        lot = self.context.lot

        if not lot:
            logger.debug('lot not found')
            raise HTTPNotFound()

        sales_segment = lot.sales_segment

        return dict(
            event=event,
            lot=lot,
            sales_segment=sales_segment,
            option_index=len(api.get_options(self.request)) + 1
            )

    @view_config(route_name='lots.entry.step1', renderer=selectable_renderer("mobile/%(membership)s/step1.html"))
    def step1(self):
        event = self.context.event
        lot = self.context.lot

        if not lot:
            logger.debug('lot not found')
            raise HTTPNotFound()

        if self.context.option_index is None:
            return HTTPFound(self.request.route_path('lots.entry.step3', event_id=event.id, lot_id=lot.id))

        return dict(
            event=event,
            lot=lot,
            sales_segment=lot.sales_segment,
            performances=lot.performances,
            option_index=self.context.option_index
            )

    @view_config(route_name='lots.entry.step2', renderer=selectable_renderer("mobile/%(membership)s/step2.html"))
    def step2(self):
        event = self.context.event
        lot = self.context.lot

        if not lot:
            logger.debug('lot not found')
            raise HTTPNotFound()

        sales_segment = lot.sales_segment

        performance = self.context.performance
        if not performance:
            logger.debug('performance not found')
            raise HTTPNotFound()


        return dict(
            event=event,
            lot=lot,
            sales_segment=sales_segment,
            performance=performance,
            products=DBSession.query(Product) \
                .filter(Product.sales_segment_id == sales_segment.id) \
                .filter(Product.performance_id == performance.id) \
                .order_by(Product.display_order).all(),
            option_index=self.context.option_index,
            messages=self.request.session.pop_flash()
            )

    def step3_rendered_value(self, option_index):
        event = self.context.event
        lot = self.context.lot
        sales_segment = lot.sales_segment

        return dict(
            event=event,
            lot=lot,
            sales_segment=sales_segment,
            option_index=option_index,
            options=[
                dict(
                    performance=Performance.query.filter_by(id=data['performance_id']).one(),
                    wished_products=[
                        dict(
                            product=Product.query.filter_by(id=rec['product_id']).one(),
                            **rec
                            )
                        for rec in data['wished_products']
                        ]
                    )
                for data in api.get_options(self.request)
                ]
            )

    @view_config(route_name='lots.entry.step3', request_method='GET', renderer=selectable_renderer("mobile/%(membership)s/step3.html"))
    def step3(self):
        return self.step3_rendered_value(len(api.get_options(self.request)))

    @back(mobile=back_to_step1)
    @view_config(route_name='lots.entry.step3', request_method='POST', renderer=selectable_renderer("mobile/%(membership)s/step3.html"))
    def step3_post(self):
        event = self.context.event
        lot = self.context.lot

        if not lot:
            logger.debug('lot not found')
            raise HTTPNotFound()

        sales_segment = lot.sales_segment

        performance = self.context.performance
        if not performance:
            logger.debug('performance not found')
            raise HTTPNotFound()

        option_index_zb = self.context.option_index - 1

        wished_products = []

        try:
            for k, v in self.request.params.items():
                if k.startswith('product-'):
                    product = Product.query \
                        .filter(Performance.id == performance.id) \
                        .filter(Product.id == k[8:]) \
                        .one()
                    quantity = max(int(v), 0) if v else 0
                    wished_products.append(dict(
                        wish_order=option_index_zb,
                        product_id=product.id,
                        quantity=quantity))
        except (ValueError, KeyError, NoResultFound):
            raise HTTPBadRequest()


        options = api.get_options(self.request)
        if len(options) < option_index_zb:
            raise HTTPBadRequest()

        try:
            total_quantity = sum(rec['quantity'] for rec in wished_products)
            if total_quantity > sales_segment.upper_limit:
                raise ValidationError(u"希望数の合計値が上限を越えています")
            elif total_quantity == 0:
                raise ValidationError(u"希望数が指定されていません")
        except ValidationError as e:
            self.request.session.flash(e.message)
            return HTTPFound(self.request.route_path(
                'lots.entry.step2',
                event_id=event.id,
                lot_id=lot.id,
                option_index=option_index_zb + 1,
                _query=dict(performance_id=performance.id)))

        option_data = dict(
            performance_id=performance.id,
            wished_products=wished_products
            )

        options[option_index_zb] = option_data

        return self.step3_rendered_value(option_index_zb + 1)

    def step4_rendered_value(self, form):
        event = self.context.event
        lot = self.context.lot

        if not lot:
            logger.debug('lot not found')
            raise HTTPNotFound()

        sales_segment = lot.sales_segment
        return dict(
            event=event,
            lot=lot,
            sales_segment=sales_segment,
            payment_delivery_methods=sales_segment.payment_delivery_method_pairs,
            form=form
            )

    @view_config(route_name='lots.entry.step4', renderer=selectable_renderer("mobile/%(membership)s/step4.html"))
    def step4(self):
        return self.step4_rendered_value(schemas.ClientForm())

    @back(mobile=back_to_step3)
    @view_config(route_name='lots.entry.step4', request_method='POST', renderer=selectable_renderer("mobile/%(membership)s/step4.html"))
    def step4_post(self):
        event = self.context.event
        lot = self.context.lot

        if not lot:
            logger.debug('lot not found')
            raise HTTPNotFound()

        sales_segment = lot.sales_segment
        cform = schemas.ClientForm(self.request.params)

        payment_delivery_method_pair_id = None
        try:
            payment_delivery_method_pair_id = long(self.request.params.get('payment_delivery_method_pair_id'))
        except (ValueError, TypeError):
            pass

        payment_delivery_pairs = sales_segment.payment_delivery_method_pairs
        if payment_delivery_method_pair_id not in [m.id for m in payment_delivery_pairs]:
            self.request.session.flash(u"お支払お引き取り方法を選択してください")
            return self.step4_rendered_value(form=cform)
        if not cform.validate():
            return self.step4_rendered_value(cform)

        shipping_address_dict = cform.get_validated_address_data()
        api.new_lot_entry(
            self.request,
            wishes=api.get_options(self.request),
            payment_delivery_method_pair_id=payment_delivery_method_pair_id,
            shipping_address_dict=shipping_address_dict,
            gender=cform['sex'].data,
            birthday=datetime(int(cform['year'].data),
                              int(cform['month'].data),
                              int(cform['day'].data)),
            memo=cform['memo'].data)

        location = urls.entry_confirm(self.request)
        return HTTPFound(location=location)
