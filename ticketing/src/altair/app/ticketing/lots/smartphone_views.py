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
from altair.app.ticketing.users.models import UserPointAccountTypeEnum

from . import api
from . import helpers as h
from . import schemas
from .exceptions import NotElectedException, OverEntryLimitException, OverEntryLimitPerPerformanceException
from .models import (
    LotEntry,
)
from . import urls
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
        if "last_name" in self.request.params:
            # 購入者情報が入っている場合のフォーム作成
            return utils.create_form(self.request, self.context, **kwds)

        return utils.create_form(self.request, self.context, None)

    @lbr_view_config(route_name='lots.entry.index', request_method="GET", renderer=selectable_renderer("index.html"))
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
        form = self._create_form(formdata=UnicodeMultiDictAdapter(self.request.params, 'utf-8', 'replace'))

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
        payment_delivery_pairs = sales_segment.payment_delivery_method_pairs

        return dict(form=form, event=event, lot=lot,
            payment_delivery_pairs=payment_delivery_pairs, wishes=wishes,
            payment_delivery_method_pair_id=self.request.params.get('payment_delivery_method_pair_id'))

    @lbr_view_config(route_name='lots.entry.sp_step3', renderer=selectable_renderer("step3.html"), custom_predicates=())
    def step3(self):
        """
        申し込み確認
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

            query = dict(self.request.params)
            for cnt, wish in enumerate(wishes):
                wish_order = wish['wished_products'][0]['wish_order']
                performance_id = wishes[cnt]['performance_id']
                product_id = wish['wished_products'][0]['product_id']
                quantity = wish['wished_products'][0]['quantity']
                query.update({'wish_order-' + str(wish_order) + '-performance_id' : performance_id})
                query.update({'wish_order-' + str(wish_order) + '-product_id' : product_id})
                query.update({'wish_order-' + str(wish_order) + '-quantity' : quantity})
            return HTTPFound(self.request.route_path(
                'lots.entry.sp_step2', event_id=event.id, lot_id=lot.id, _query=query))

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
        formdata = MultiDict(
            accountno=""
            )
        form = cart_schemas.PointForm(formdata=formdata)
        lot_asid = self.request.context.lot_asid

        accountno = self.request.params.get('account')
        user = cart_api.get_or_create_user(self.context.authenticated_user())
        if accountno:
            form['accountno'].data = accountno.replace('-', '')
        else:
            if api.enable_auto_input_form(self.request, user) and user:
                acc = cart_api.get_user_point_account(user.id)
                form['accountno'].data = acc.account_number.replace('-', '') if acc else ""

        return dict(
            form=form,
            asid=lot_asid
        )
        return dict()

    @lbr_view_config(request_method="POST", route_name='lots.entry.rsp', renderer=selectable_renderer("point.html"), custom_predicates=())
    def rsp_post(self):
        form = cart_schemas.PointForm(formdata=self.request.params)
        point_params = dict(
            accountno=form.data['accountno'],
            )

        if not form.validate():
            asid = self.request.context.asid_smartphone
            return dict(form=form, asid=asid)

        if cart_api.is_point_input_required(self.context, self.request):
            point = point_params.pop("accountno", None)
            user = cart_api.get_or_create_user(self.context.authenticated_user())
            if point:
                if not user:
                    user = cart_api.get_or_create_user_from_point_no(point)

                cart_api.create_user_point_account_from_point_no(
                    user.id,
                    type=UserPointAccountTypeEnum.Rakuten,
                    account_number=point
                    )
                api.set_point_user(self.request, user)

        from .adapters import LotSessionCart
        from altair.app.ticketing.payments.payment import Payment
        entry = api.get_lot_entry_dict(self.request)
        cart = LotSessionCart(entry, self.request, self.request.context.lot)
        payment = Payment(cart, self.request)
        # マルチ決済のみオーソリのためにカード番号入力画面に遷移する
        result = payment.call_prepare()
        if callable(result):
            return result

        return HTTPFound(self.request.route_url('lots.entry.confirm', event_id=self.request.context.event.id, lot_id=self.request.context.lot.id))
