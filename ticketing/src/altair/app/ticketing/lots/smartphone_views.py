# -*- coding:utf-8 -*-
from datetime import datetime, timedelta
import logging
import operator

from markupsafe import Markup
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPBadRequest
from sqlalchemy.orm.exc import NoResultFound

from wtforms.validators import ValidationError
from altair.mobile import mobile_view_config
from altair.pyramid_tz.api import get_timezone

from altair.app.ticketing.models import DBSession
from altair.app.ticketing.core.models import PaymentDeliveryMethodPair
from altair.app.ticketing.users import api as user_api
from altair.app.ticketing.utils import toutc
from altair.app.ticketing.payments.payment import Payment
from altair.app.ticketing.cart.exceptions import NoCartError
from altair.app.ticketing.mailmags.api import get_magazines_to_subscribe, multi_subscribe
from altair.app.ticketing.cart.api import is_smartphone, is_smartphone_organization

from . import api
from . import helpers as h
from . import schemas
from . import selectable_renderer
from .exceptions import NotElectedException
from .models import (
    LotEntry,
)
from .adapters import LotSessionCart
from . import urls

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

def get_nogizaka_lot_ids(request):
    try:
        return [long(id) for id in request.registry.settings.get('altair.lots.nogizaka_lot_id').split(',')]
    except:
        return []

def is_nogizaka(context, request):
    if request.method != 'POST':
        return False
    lot = getattr(context, 'lot')
    if not lot or lot.id not in get_nogizaka_lot_ids(request):
        return False
    return True

def nogizaka_auth(context, request):
    lot = getattr(context, 'lot')
    if not lot or lot.id not in get_nogizaka_lot_ids(request):
        return True
    if request.session.get('lots.passed.keyword'):
        return True
    return False

@view_defaults(request_type='altair.mobile.interfaces.ISmartphoneRequest',
               permission="lots", custom_predicates=(is_smartphone_organization))
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

    def _create_form(self):
        return api.create_client_form(self.context)

    @view_config(route_name='lots.entry.index', renderer=selectable_renderer("smartphone/%(membership)s/index.html"), custom_predicates=(nogizaka_auth, ))
    def index(self):
        """
        イベント詳細
        """
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

    @view_config(route_name='lots.entry.sp_step1', renderer=selectable_renderer("smartphone/%(membership)s/step1.html"), custom_predicates=(nogizaka_auth, ))
    def step1(self, form=None):
        """
        抽選第N希望まで選択
        """
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

        return dict(form=form, event=event, sales_segment=sales_segment,
            posted_values=dict(self.request.POST),
            performance_product_map=performance_product_map,
            stock_types=stock_types,
            selected_performance=selected_performance,
            lot=lot, performances=performances, performance_map=performance_map)


    @view_config(route_name='lots.entry.sp_step2', renderer=selectable_renderer("smartphone/%(membership)s/step2.html"), custom_predicates=(nogizaka_auth, ))
    def step2(self, form=None):
        """
        購入情報入力
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

        wishes = h.convert_wishes(self.request.params, lot.limit_wishes)

        validated = True

        # 商品チェック
        if not wishes:
            self.request.session.flash(u"申し込み内容に入力不備があります")
            validated = False
        elif not h.check_duplicated_products(wishes):
            self.request.session.flash(u"同一商品が複数回希望されています。")
            validated = False
        elif not h.check_quantities(wishes, lot.upper_limit):
            self.request.session.flash(u"各希望ごとの合計枚数は最大{0}枚までにしてください".format(lot.upper_limit))
            validated = False

        if not validated:
            return HTTPFound(self.request.route_path(
                'lots.entry.sp_step1', event_id=event.id, lot_id=lot.id))

        form = self._create_form()

        sales_segment = lot.sales_segment
        payment_delivery_pairs = sales_segment.payment_delivery_method_pairs

        return dict(form=form, event=event, lot=lot,
            payment_delivery_pairs=payment_delivery_pairs, wishes=wishes,
            payment_delivery_method_pair_id=self.request.params.get('payment_delivery_method_pair_id'))

    @view_config(route_name='lots.entry.sp_step3', renderer=selectable_renderer("smartphone/%(membership)s/step3.html"), custom_predicates=(nogizaka_auth, ))
    def step3(self, form=None):
        """
        申し込み確認
        """
        lot = self.context.lot
        if not lot:
            logger.debug('lot not not found')
            raise HTTPNotFound()

        performances = lot.performances
        if not performances:
            logger.debug('lot performances not found')
            raise HTTPNotFound()


        cform = schemas.ClientForm(formdata=self.request.params)
        sales_segment = lot.sales_segment
        payment_delivery_pairs = sales_segment.payment_delivery_method_pairs
        payment_delivery_method_pair_id = self.request.params.get('payment_delivery_method_pair_id')
        wishes = h.convert_sp_wishes(self.request.params, lot.limit_wishes)

        validated = True
        email = self.request.params.get('email_1')
        # 申込回数チェック
        if not lot.check_entry_limit(email):
            self.request.session.flash(u"抽選への申込は{0}回までとなっております。".format(lot.entry_limit))
            validated = False

        # 決済・引取方法選択
        if payment_delivery_method_pair_id not in [str(m.id) for m in payment_delivery_pairs]:
            self.request.session.flash(u"お支払お引き取り方法を選択してください")
            validated = False

        birthday = None
        try:
            birthday = datetime(int(cform['year'].data),
                                int(cform['month'].data),
                                int(cform['day'].data))
        except (ValueError, TypeError):
            pass

        # 購入者情報
        if not cform.validate() or not birthday:
            self.request.session.flash(u"購入者情報に入力不備があります")
            if not birthday:
                cform['year'].errors = [u'日付が正しくありません']
            validated = False

        if not validated:
            return self.get(form=cform)

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
            memo=cform['memo'].data)

        entry = self.request.session.get('lots.entry')
        if entry is None:
            self.request.session.flash(u"セッションに問題が発生しました。")
            return self.back_to_form()

        self.request.session['lots.entry.time'] = datetime.now()
        cart = LotSessionCart(entry, self.request, self.context.lot)

        payment = Payment(cart, self.request)
        self.request.session['payment_confirm_url'] = urls.entry_confirm(self.request)

        result = payment.call_prepare()
        if callable(result):
            return result

        location = urls.entry_confirm(self.request)
        return HTTPFound(location=location)
