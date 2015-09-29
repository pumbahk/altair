# -*- coding:utf-8 -*-
from datetime import datetime, timedelta
import logging
import operator

from markupsafe import Markup
from pyramid.view import view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPBadRequest
from sqlalchemy.orm.exc import NoResultFound
from webob.multidict import MultiDict

from wtforms.validators import ValidationError
from altair.now import get_now
from altair.pyramid_tz.api import get_timezone
from altair.pyramid_dynamic_renderer import lbr_view_config
from altair.request.adapters import UnicodeMultiDictAdapter
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.core.models import PaymentDeliveryMethodPair
from altair.app.ticketing.utils import toutc
from altair.app.ticketing.cart.exceptions import NoCartError
from altair.app.ticketing.mailmags.api import get_magazines_to_subscribe, multi_subscribe
from altair.app.ticketing.cart import api as cart_api
from altair.app.ticketing.cart import schemas as cart_schemas
from altair.app.ticketing.cart.rendering import selectable_renderer
from altair.app.ticketing.cart.view_support import render_view_to_response_with_derived_request

from . import api
from . import helpers as h
from . import schemas
from .exceptions import NotElectedException, OverEntryLimitException, OverEntryLimitPerPerformanceException
from .models import (
    LotEntry,
)
from . import urls
from altair.app.ticketing.cart.views import jump_maintenance_page_for_trouble
from . import utils

logger = logging.getLogger(__name__)

def make_performance_map(request, performances):
    tz = get_timezone(request)
    performance_map = {}
    for performance in performances:
        performances_per_name = performance_map.get(performance.name)
        if not performances_per_name:
            performances_per_name = performance_map[performance.name] = []
        performances_per_name.append(
            dict(
                id=performance.id,
                name=performance.name,
                venue=performance.venue.name,
                open_on=toutc(performance.open_on, tz).isoformat() if performance.open_on else None,
                start_on=toutc(performance.start_on, tz).isoformat() if performance.start_on else None,
                label=h.performance_date_label(performance)
                )
            )

    for k in performance_map:
        v = performance_map[k]
        performance_map[k] = sorted(v,
                                    key=lambda x: (x['start_on'], x['id']))

    retval = list(performance_map.iteritems())
    retval = sorted(retval, key=lambda x: (x[1][0]['start_on'], x[1][0]['id']))

    return retval


@view_defaults(request_type='altair.mobile.interfaces.ISmartphoneRequest',
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

    def _create_performance_product_map(self, products):
        performance_product_map = {}
        for product in products:
            performance = product.performance
            products = performance_product_map.get(performance.id, [])
            products.append(dict(
                id=product.id,
                name=product.name,
                display_order=product.display_order,
                stock_type_id=product.seat_stock_type_id,
                price=float(product.price),
                formatted_price=h.format_currency(product.price),
                description=product.description,
            ))
            performance_product_map[performance.id] = products

        key_func = operator.itemgetter('display_order', 'id')
        for p in performance_product_map.values():
            p.sort(key=key_func)
        return performance_product_map

    def _create_form(self, **kwds):
        """希望入力と配送先情報と追加情報入力用のフォームを返す
        """
        return utils.create_form(self.request, self.context, **kwds)

    @lbr_view_config(route_name='lots.entry.index', request_method="GET", renderer=selectable_renderer("index.html"))
    def index(self):
        """
        イベント詳細
        """
        jump_maintenance_page_for_trouble(self.request.organization)

        event = self.context.event
        lot = self.context.lot

        if not lot:
            logger.debug('lot not found')
            raise HTTPNotFound()

        performance_id = self.request.params.get('performance')

        return dict(
            event=event,
            lot=lot,
            performance_id = performance_id,
            sales_segment=lot.sales_segment,
            performances=sorted(lot.performances, lambda a, b: cmp(a.start_on, b.start_on)),
            )

    @lbr_view_config(route_name='lots.entry.sp_step1', renderer=selectable_renderer("step1.html"))
    def step1(self):
        """
        抽選第N希望まで選択
        """
        event = self.context.event
        lot = self.context.lot

        if not lot:
            logger.debug('lot not not found')
            raise HTTPNotFound()

        performances = lot.performances
        if not performances:
            logger.debug('lot performances not found')
            raise HTTPNotFound()
        performances = sorted(performances, key=operator.attrgetter('start_on'))

        performance_map = make_performance_map(self.request, performances)

        performance_id = self.request.params.get('performance')
        selected_performance = None
        if performance_id:
            for p in lot.performances:
                if str(p.id) == performance_id:
                    selected_performance = p
                    break

        sales_segment = lot.sales_segment
        performance_product_map = self._create_performance_product_map(sales_segment.products)
        stock_types = [
            dict(
                id=rec[0],
                name=rec[1],
                display_order=rec[2],
                description=rec[3]
                )
            for rec in sorted(
                set(
                    (
                        product.seat_stock_type_id,
                        product.seat_stock_type.name,
                        product.seat_stock_type.display_order,
                        product.seat_stock_type.description
                        )
                    for product in sales_segment.products
                    ),
                lambda a, b: cmp(a[2], b[2])
                )
            ]

        return dict(event=event, sales_segment=sales_segment,
            posted_values=dict(self.request.POST),
            performance_product_map=performance_product_map,
            stock_types=stock_types,
            selected_performance=selected_performance,
            lot=lot, performances=performances, performance_map=performance_map)


    @lbr_view_config(route_name='lots.entry.sp_step2', renderer=selectable_renderer("step2.html"), custom_predicates=())
    def step2(self):
        """
        購入情報入力
        """
        form = self.request.environ.get('cform')
        if form is None:
            form = self._create_form()

        event = self.context.event
        lot = self.context.lot

        if not lot:
            logger.debug('lot not not found')
            raise HTTPNotFound()

        performances = lot.performances
        if not performances:
            logger.debug('lot performances not found')
            raise HTTPNotFound()

        wishes = h.convert_wishes(self.request.params, lot.limit_wishes)
        logger.debug('wishes={0}'.format(wishes))

        validated = True

        # 商品チェック
        if not wishes:
            self.request.session.flash(u"申し込み内容に入力不備があります")
            validated = False
        elif not h.check_duplicated_products(wishes):
            self.request.session.flash(u"同一商品が複数回希望されています。")
            validated = False
        elif not h.check_quantities(wishes, lot.max_quantity):
            self.request.session.flash(u"各希望ごとの合計枚数は最大{0}枚までにしてください".format(lot.max_quantity))
            validated = False
        elif not h.check_valid_products(wishes):
            logger.debug('Product.performance_id mismatch')
            self.request.session.flash(u"選択された券種が見つかりません。もう一度はじめから選択してください。")
            validated = False

        if not validated:
            return HTTPFound(self.request.route_path(
                'lots.entry.sp_step1', event_id=event.id, lot_id=lot.id))

        sales_segment = lot.sales_segment
        payment_delivery_pairs = [pdmp for pdmp in sales_segment.payment_delivery_method_pairs if pdmp.public]

        return dict(form=form, event=event, lot=lot,
            payment_delivery_pairs=payment_delivery_pairs, wishes=wishes,
            payment_delivery_method_pair_id=self.request.params.get('payment_delivery_method_pair_id'))

    @lbr_view_config(route_name='lots.entry.sp_step3', renderer=selectable_renderer("step3.html"), custom_predicates=())
    def step3(self):
        """
        申し込み確認
        """
        self.request.session.pop_flash()
        event = self.context.event
        lot = self.context.lot
        if not lot:
            logger.debug('lot not not found')
            raise HTTPNotFound()

        performances = lot.performances
        if not performances:
            logger.debug('lot performances not found')
            raise HTTPNotFound()
        cform = self._create_form(formdata=UnicodeMultiDictAdapter(self.request.params, 'utf-8', 'replace'))
        sales_segment = lot.sales_segment
        payment_delivery_pairs = sales_segment.payment_delivery_method_pairs
        payment_delivery_method_pair_id = self.request.params.get('payment_delivery_method_pair_id')
        wishes = h.convert_wishes(self.request.params, lot.limit_wishes)
        logger.debug('wishes={0}'.format(wishes))

        validated = True
        user = cart_api.get_user(self.context.authenticated_user())
        # 申込回数チェック
        try:
            self.context.check_entry_limit(wishes, user=user, email=cform.email_1.data)
        except OverEntryLimitPerPerformanceException as e:
            self.request.session.flash(u"公演「{0}」への申込は{1}回までとなっております。".format(e.performance_name, e.entry_limit))
            validated = False
        except OverEntryLimitException as e:
            self.request.session.flash(u"抽選への申込は{0}回までとなっております。".format(e.entry_limit))
            validated = False

        # 決済・引取方法選択
        if payment_delivery_method_pair_id not in [str(m.id) for m in payment_delivery_pairs]:
            self.request.session.flash(u"お支払お引き取り方法を選択してください")
            validated = False

        birthday = cform['birthday'].data

        # 購入者情報
        if not cform.validate() or not birthday:
            self.request.session.flash(u"購入者情報に入力不備があります")
            if not birthday:
                cform['birthday'].errors = [u'日付が正しくありません']
            validated = False

        if not validated:
            for k, errors in cform.errors.items():
                if isinstance(errors, dict):
                    for k, errors in errors.items():
                        for error in errors:
                            self.request.session.flash(u'%s: %s' % (schemas.client_form_fields.get(k, k), error))
                else:
                    for error in errors:
                        self.request.session.flash(u'%s: %s' % (schemas.client_form_fields.get(k, k), error))

            def retoucher(subrequest):
                subrequest.session = self.request.session
                subrequest.environ['cform'] = cform

            return render_view_to_response_with_derived_request(
                context_factory=lambda request: self.context,
                request=self.request,
                retoucher=retoucher,
                route=('lots.entry.sp_step2', self.request.matchdict)
                )

        entry_no = api.generate_entry_no(self.request, self.context.organization)

        shipping_address_dict = cform.get_validated_address_data()
        api.new_lot_entry(
            self.request,
            entry_no=entry_no,
            wishes=wishes,
            payment_delivery_method_pair_id=payment_delivery_method_pair_id,
            shipping_address_dict=shipping_address_dict,
            gender=cform['sex'].data,
            birthday=birthday,
            memo=cform['memo'].data,
            extra=cform['extra'].data,
            )

        entry = api.get_lot_entry_dict(self.request)
        if entry is None:
            self.request.session.flash(u"セッションに問題が発生しました。")
            return self.back_to_form()

        self.request.session['lots.entry.time'] = get_now(self.request)
        if cart_api.is_point_input_required(self.context, self.request):
            return HTTPFound(self.request.route_path('lots.entry.rsp'))
        result = api.prepare1_for_payment(self.request, entry)
        if callable(result):
            return result
        return HTTPFound(urls.entry_confirm(self.request))

    @lbr_view_config(request_method="GET", route_name='lots.entry.rsp', renderer=selectable_renderer("point.html"), custom_predicates=())
    def rsp(self):
        lot_asid = self.context.lot_asid_smartphone
        return self.context.get_rsp(lot_asid)

    @lbr_view_config(request_method="POST", route_name='lots.entry.rsp', renderer=selectable_renderer("point.html"), custom_predicates=())
    def rsp_post(self):
        lot_asid = self.context.lot_asid_smartphone
        return self.context.post_rsp(lot_asid)
