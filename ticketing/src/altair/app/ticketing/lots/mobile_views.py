# -*- coding:utf-8 -*-
from datetime import datetime
import logging
from markupsafe import Markup

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPBadRequest
from sqlalchemy.orm.exc import NoResultFound
from wtforms.validators import ValidationError
from altair.now import get_now
from altair.pyramid_dynamic_renderer import lbr_view_config
from altair.request.adapters import UnicodeMultiDictAdapter
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.core.models import PaymentDeliveryMethodPair, Performance, Product
from altair.app.ticketing.cart import api as cart_api
from altair.app.ticketing.cart.exceptions import NoCartError
from altair.app.ticketing.cart.views import back
from altair.app.ticketing.cart.rendering import selectable_renderer
from . import api
from . import helpers as h
from . import schemas
from .exceptions import NotElectedException, OverEntryLimitException, OverEntryLimitPerPerformanceException
from .models import (
    LotEntry,
    LotEntryWish,
    LotElectedEntry,
)
from . import urls
from altair.app.ticketing.cart.views import jump_maintenance_page_for_trouble
from . import utils

logger = logging.getLogger(__name__)


@lbr_view_config(request_type='altair.mobile.interfaces.IMobileRequest',
                 context=NoResultFound)
def no_results_found(context, request):
    """ 改良が必要。ログに該当のクエリを出したい。 """
    logger.warning(context)
    return HTTPNotFound()


def back_to_step1(request):
    context = request.context
    return HTTPFound(request.route_path('lots.entry.step1', event_id=context.event.id, lot_id=context.lot.id, option_index=context.option_index))

def back_to_step3(request):
    context = request.context
    return HTTPFound(request.route_path('lots.entry.step3', event_id=context.event.id, lot_id=context.lot.id))


@view_defaults(request_type='altair.mobile.interfaces.IMobileRequest',
               permission="lots")
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

    def cr2br(self, t):
        return h.cr2br(t)

    @lbr_view_config(route_name='lots.entry.index', request_method="GET", renderer=selectable_renderer("index.html"))
    def index(self):
        jump_maintenance_page_for_trouble(self.request.organization)

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
            option_index=len(api.get_options(self.request, lot.id)) + 1
            )

    def _create_form(self, **kwds):
        """希望入力と配送先情報と追加情報入力用のフォームを返す
        """
        return utils.create_form(self.request, self.context, **kwds)

    @lbr_view_config(route_name='lots.entry.step1', renderer=selectable_renderer("step1.html"))
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
            performances=sorted(lot.performances, lambda a, b: cmp(a.start_on, b.start_on)),
            option_index=self.context.option_index
            )

    @lbr_view_config(route_name='lots.entry.step2', renderer=selectable_renderer("step2.html"))
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

        products = {}
        for product in DBSession.query(Product) \
                .join(Product.seat_stock_type) \
                .filter(Product.sales_segment_id == sales_segment.id) \
                .filter(Product.performance_id == performance.id) \
                .order_by(Product.display_order):
            products_per_stock_type = products.get(product.seat_stock_type_id)
            if products_per_stock_type is None:
                products_per_stock_type = products[product.seat_stock_type_id] = []
            products_per_stock_type.append(product)

        return dict(
            event=event,
            lot=lot,
            sales_segment=sales_segment,
            performance=performance,
            products=sorted(
                [
                    products_per_stock_type
                    for _, products_per_stock_type in products.items()
                    ],
                lambda a, b: cmp(a[0].seat_stock_type.display_order, a[0].seat_stock_type.display_order,)
                ),
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
            options=h.decorate_options_mobile(api.get_options(self.request, lot.id))
            )

    @lbr_view_config(route_name='lots.entry.step3', request_method='GET', renderer=selectable_renderer("step3.html"))
    def step3(self):
        lot = self.context.lot
        option_index = len(api.get_options(self.request, lot.id))
        if option_index == 0:
            return HTTPFound(self.request.route_path('lots.entry.index', event_id=self.context.event.id, lot_id=lot.id))
        return self.step3_rendered_value(option_index)

    @back(mobile=back_to_step1)
    @lbr_view_config(route_name='lots.entry.step3', request_method='POST', renderer=selectable_renderer("step3.html"))
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
                    if quantity > 0:
                        wished_products.append(dict(
                            wish_order=option_index_zb,
                            seat_stock_type_id=product.seat_stock_type_id,
                            product_id=product.id,
                            quantity=quantity))
        except (ValueError, KeyError, NoResultFound):
            import sys
            logger.error('could not parse request', exc_info=sys.exc_info())
            raise HTTPBadRequest()


        options = api.get_options(self.request, lot.id)
        if len(options) < option_index_zb:
            logger.error('too few options')
            raise HTTPBadRequest()

        try:
            total_quantity = sum(rec['quantity'] for rec in wished_products)
            if total_quantity > sales_segment.max_quantity:
                raise ValidationError(u"希望数の合計値が上限を越えています")
            elif total_quantity == 0:
                raise ValidationError(u"希望数が指定されていません")
            elif len(set(wished_product['seat_stock_type_id'] for wished_product in wished_products)) > 1:
                raise ValidationError(u"複数席種の選択はできません")
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
        wishes = options
        logger.debug('option_data={0}'.format(option_data))

        # 商品チェック
        validated = True
        if not wishes:
            self.request.session.flash(u"申し込み内容に入力不備があります")
            validated = False
        elif not h.check_duplicated_products(wishes):
            self.request.session.flash(u"同一商品が複数回希望されています。")
            validated = False
        elif not h.check_quantities(wishes, lot.max_quantity):
            self.request.session.flash(u"各希望ごとの合計枚数は最大{0}枚までにしてください".format(lot.max_quantity))
            validated = False

        if not validated:
            del options[option_index_zb]
            return HTTPFound(self.request.route_path(
                'lots.entry.step2',
                event_id=event.id,
                lot_id=lot.id,
                option_index=option_index_zb + 1,
                _query=dict(performance_id=performance.id)))

        return self.step3_rendered_value(option_index_zb + 1)

    def step4_rendered_value(self, form, pdmp_messages=None):
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
            form=form,
            pdmp_messages=pdmp_messages,
            messages=self.request.session.pop_flash()
            )

    @lbr_view_config(route_name='lots.entry.step4', renderer=selectable_renderer("step4.html"))
    def step4(self):
        cform = self._create_form()
        return self.step4_rendered_value(cform)

    @back(mobile=back_to_step3)
    @lbr_view_config(route_name='lots.entry.step4', request_method='POST', renderer=selectable_renderer("step4.html"))
    def step4_post(self):
        event = self.context.event
        lot = self.context.lot

        if not lot:
            logger.debug('lot not found')
            raise HTTPNotFound()

        sales_segment = lot.sales_segment
        cform = self._create_form(formdata=UnicodeMultiDictAdapter(self.request.params, 'utf-8', 'replace'))
        payment_delivery_method_pair_id = None
        try:
            payment_delivery_method_pair_id = long(self.request.params.get('payment_delivery_method_pair_id'))
        except (ValueError, TypeError):
            pass

        validated = True
        pdmp_messages = None
        wishes=api.get_options(self.request, lot.id)
        logger.debug('wishes={0}'.format(wishes))

        payment_delivery_pairs = sales_segment.payment_delivery_method_pairs
        if payment_delivery_method_pair_id not in [m.id for m in payment_delivery_pairs]:
            pdmp_messages = [u"お支払／引取方法をお選びください"]
            validated = False
        if not cform.validate():
            validated = False
        if not wishes:
            self.request.session.flash(u"申し込み内容に入力不備があります")
            validated = False

        if not validated:
            self.request.session.flash(u"入力内容を確認してください")
            return self.step4_rendered_value(form=cform, pdmp_messages=pdmp_messages)

        user = cart_api.get_user(self.context.authenticated_user())

        # 申込回数チェック
        try:
            self.context.check_entry_limit(wishes, user=user, email=cform.email_1.data)
        except OverEntryLimitPerPerformanceException as e:
            self.request.session.flash(u"公演「{0}」への申込は{1}回までとなっております。".format(e.performance_name, e.entry_limit))
            return self.step4_rendered_value(form=cform, pdmp_messages=pdmp_messages)
        except OverEntryLimitException as e:
            self.request.session.flash(u"抽選への申込は{0}回までとなっております。".format(e.entry_limit))
            return self.step4_rendered_value(form=cform, pdmp_messages=pdmp_messages)

        entry_no = api.generate_entry_no(self.request, self.context.organization)
        shipping_address_dict = cform.get_validated_address_data()
        api.new_lot_entry(
            self.request,
            entry_no=entry_no,
            wishes=wishes,
            payment_delivery_method_pair_id=payment_delivery_method_pair_id,
            shipping_address_dict=shipping_address_dict,
            gender=cform['sex'].data,
            birthday=cform['birthday'].data,
            memo=cform['memo'].data,
            extra=cform['extra'].data,
            )
        entry = api.get_lot_entry_dict(self.request)
        self.request.session['lots.entry.time'] = get_now(self.request)

        if cart_api.is_point_input_required(self.context, self.request):
            return HTTPFound(self.request.route_path('lots.entry.rsp'))

        result = api.prepare1_for_payment(self.request, entry)
        if callable(result):
            return result

        location = urls.entry_confirm(self.request)
        return HTTPFound(location=location)
