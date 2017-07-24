# -*- coding:utf-8 -*-
from datetime import datetime, timedelta
import logging
import operator
import urlparse

from markupsafe import Markup
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPBadRequest, HTTPMovedPermanently
from sqlalchemy.orm.exc import NoResultFound

from wtforms.validators import ValidationError
from altair.pyramid_tz.api import get_timezone
from altair.pyramid_dynamic_renderer import lbr_view_config
from altair.pyramid_dynamic_renderer.config import lbr_notfound_view_config
from altair.request.adapters import UnicodeMultiDictAdapter
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.core.models import PaymentDeliveryMethodPair
from altair.app.ticketing.cart import api as cart_api
from altair.app.ticketing.utils import toutc
from altair.app.ticketing.cart.exceptions import NoCartError
from altair.app.ticketing.cart.view_support import (
    get_extra_form_data_pair_pairs,
    coerce_extra_form_data,
    )
from altair.app.ticketing.mailmags.api import get_magazines_to_subscribe, multi_subscribe
from altair.app.ticketing.cart.rendering import selectable_renderer
from altair.now import get_now
from . import api
from . import helpers as h
from . import schemas
from .exceptions import NotElectedException, OverEntryLimitException, OverEntryLimitPerPerformanceException
from .models import (
    LotEntry,
)
from .adapters import (
    LotSessionCart,
    LotEntryController
)
from .rendering import selectable_renderer
from .utils import add_session_clear_query
from . import urls
from altair.app.ticketing.cart.views import jump_maintenance_page_for_trouble
from altair.app.ticketing.orderreview.views import (
    jump_maintenance_page_om_for_trouble,
    jump_infomation_page_om_for_10873,
    )
from . import utils, utils_i18n
from pyramid.session import check_csrf_token
from altair.app.ticketing.mails.api import get_mail_utility
from altair.app.ticketing.core.models import (
    MailTypeEnum,
    OrganizationSetting,
    )
from .exceptions import LotEntryWithdrawException

from altair.app.ticketing.users.word import word_subscribe
from altair.app.ticketing.i18n import custom_locale_negotiator
from functools import partial
logger = logging.getLogger(__name__)

LOT_ENTRY_ATTRIBUTE_SESSION_KEY = 'lot.entry.attribute'


def make_performance_map(request, performances):
    performances = sorted(performances, key=operator.attrgetter('start_on'))
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

def my_render_view_to_response(context, request, view_name=''):
    from pyramid.interfaces import IViewClassifier, IView
    from zope.interface import providedBy
    view_callable = request.registry.adapters.lookup(
        (IViewClassifier, request.request_iface, providedBy(context)),
        IView, name=view_name, default=None)
    if view_callable is None:
        return None
    return view_callable(context, request)

@lbr_view_config(context=NoResultFound)
def no_results_found(context, request):
    """ 改良が必要。ログに該当のクエリを出したい。 """
    logger.warning(context)
    return HTTPNotFound()

@lbr_view_config(context=NoCartError, renderer=selectable_renderer("timeout.html"))
@lbr_view_config(context=NoCartError, request_type='altair.mobile.interfaces.IMobileRequest', renderer=selectable_renderer("timeout.html"))
@lbr_view_config(context=NoCartError, request_type='altair.mobile.interfaces.ISmartphoneRequest', renderer=selectable_renderer("timeout.html"))
def no_cart_error(context, request):
    request.response.status = 404
    return {}

@lbr_view_config(route_name='rakuten_auth.error', renderer=selectable_renderer("message.html"))
@lbr_view_config(route_name='rakuten_auth.error', request_type='altair.mobile.interfaces.IMobileRequest', renderer=selectable_renderer("error.html"))
def rakuten_auth_error(context, request):
    return dict(message=u"認証に失敗しました。最初から操作をしてください。")

@view_defaults(route_name='lots.entry.agreement', permission="lots")
class AgreementLotView(object):
    def __init__(self, context, request):
        self.request = request
        self.context = context
        self._message = partial(h._message, request=self.request)

    def validate_return_to(self, url):
        _url = urlparse.urlparse(url)
        if _url.netloc and _url.netloc != self.request.host:
            return None
        return url

    @lbr_view_config(request_method="GET", renderer=selectable_renderer("agreement.html"))
    def get(self):
        event = self.context.event
        lot = self.context.lot

        if not lot:
            logger.debug('lot not found')
            raise HTTPNotFound()

        sales_segment = lot.sales_segment

        return_to = self.request.route_path('lots.entry.index', event_id=event.id, lot_id=lot.id, _query=self.request.GET)

        if not sales_segment.setting.disp_agreement:
            return HTTPFound(return_to)

        return dict(
            return_to=return_to,
            agreement_body=Markup(sales_segment.setting.agreement_body)
            )

    @lbr_view_config(request_method="POST")
    def post(self):
        event = self.context.event
        lot = self.context.lot

        if not lot:
            logger.debug('lot not found')
            raise HTTPNotFound()

        agree = self.request.params.get('agree')
        return_to = self.request.params.get('return_to')
        return_to = return_to and self.validate_return_to(return_to)

        if agree is None or return_to is None:
            self.request.session.flash(self._message(u"内容を同意の上、チェックを入れてください。"))
            return HTTPFound(self.request.route_url('lots.entry.agreement', event_id=event.id, lot_id=lot.id, _query=self.request.GET))

        return HTTPFound(return_to)


@view_defaults(route_name='lots.entry.agreement.compat', renderer=selectable_renderer("agreement.html"), permission="lots")
class CompatAgreementLotView(object):
    def __init__(self, context, request):
        self.request = request
        self.context = context

    @lbr_view_config(request_method="GET")
    def get(self):
        return HTTPMovedPermanently(self.request.route_path('lots.entry.agreement', _query=self.request.GET, **self.request.matchdict))

    @lbr_view_config(request_method="POST")
    def post(self):
        return AgreementLotView(self.context, self.request).post()


@view_defaults(route_name='lots.entry.index', renderer=selectable_renderer("index.html"), permission="lots")
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
        self._message = partial(h._message, request=self.request)

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
                min_product_quantity=product.min_product_quantity,
                max_product_quantity=product.max_product_quantity,
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

    def build_products_dict(self):
        from altair.app.ticketing.models import DBSession as session
        from markupsafe import escape, Markup
        import altair.app.ticketing.core.models as c_models
        from altair.viewhelpers.numbers import create_number_formatter
        sales_segment = self.context.lot.sales_segment
        product_query = session.query(c_models.Product) \
            .filter(c_models.Product.sales_segment_id == sales_segment.id, c_models.Product.public != False) \
            .order_by(c_models.Product.display_order)
        formatter = create_number_formatter(self.request)
        return [(p.name, Markup(u'{name} ({price})'.format(name=escape(p.name), price=formatter.format_currency_html(p.price, prefer_post_symbol=True)))) for p in product_query]

    def _create_form(self, **kwds):
        """希望入力と配送先情報と追加情報入力用のフォームを返す
        """
        return utils_i18n.create_form(self.request, self.context, **kwds)

    def _stock_type_from_products(self, products):
        return [
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
                    for product in products if product.seat_stock_type.quantity_only is True
                    ),
                lambda a, b: cmp(a[2], b[2])
                )
            ]

    @lbr_view_config(request_method="GET")
    def get(self, form=None):
        jump_maintenance_page_for_trouble(self.request.organization)
        if form is None:
            form = self._create_form()
        event = self.context.event
        lot = self.context.lot
        performances = lot.performances
        performances = sorted(performances, key=lambda p: (p.display_order, p.start_on))
        performance_map = make_performance_map(self.request, performances)

        performance_id = self.request.params.get('performance')
        selected_performance = None
        if performance_id:
            for p in lot.performances:
                if str(p.id) == performance_id:
                    selected_performance = p
                    break

        sales_segment = lot.sales_segment
        payment_delivery_pairs = [pdmp for pdmp in sales_segment.payment_delivery_method_pairs if pdmp.public]
        performance_product_map = self._create_performance_product_map(sales_segment.products)
        stock_types = self._stock_type_from_products(sales_segment.products)

        return dict(
            form=form,
            event=event,
            sales_segment=sales_segment,
            payment_delivery_pairs=payment_delivery_pairs,
            posted_values=dict(self.request.POST),
            performance_product_map=performance_product_map,
            stock_types=stock_types,
            selected_performance=selected_performance,
            payment_delivery_method_pair_id=self.request.params.get('payment_delivery_method_pair_id'),
            lot=lot,
            performances=performances,
            performance_map=performance_map,
            custom_locale_negotiator=custom_locale_negotiator(self.request) if self.request.organization.setting.i18n else ""
        )

    @lbr_view_config(request_method="POST")
    def post(self):
        """ 抽選申し込み作成(一部)
        商品、枚数チェック
        申し込み排他チェック
        - 申し込み回数
        - 申し込み内の公演、席種排他チェック
        """
        jump_maintenance_page_for_trouble(self.request.organization)

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
            self.request.session.flash(self._message(u"公演「{0}」への申込は{1}回までとなっております。").format(e.performance_name, e.entry_limit))
            validated = False
        except OverEntryLimitException as e:
            self.request.session.flash(self._message(u"抽選への申込は{0}回までとなっております。").format(e.entry_limit))
            validated = False

        # 商品チェック
        if not wishes:
            self.request.session.flash(self._message(u"申し込み内容に入力不備があります"))
            validated = False
        elif not h.check_duplicated_products(wishes):
            self.request.session.flash(self._message(u"同一商品が複数回希望されています。"))
            validated = False
        elif not h.check_quantities(wishes, lot.max_quantity):
            self.request.session.flash(self._message(u"各希望ごとの合計枚数は最大{0}枚までにしてください").format(lot.max_quantity))
            validated = False
        elif not h.check_valid_products(wishes):
            logger.debug('Product.performance_id mismatch')
            self.request.session.flash(self._message(u"選択された券種が見つかりません。もう一度はじめから選択してください。"))
            validated = False

        # 決済・引取方法選択
        if payment_delivery_method_pair_id not in [str(m.id) for m in payment_delivery_pairs]:
            self.request.session.flash(self._message(u"お支払お引き取り方法を選択してください"))
            validated = False

        email_1 = cform['email_1'].data
        birthday = cform['birthday'].data

        # 購入者情報
        # tkt3443: lotsでメールアドレスの入力を64文字以下で制限するバリデーションを入れる
        if email_1 and len(email_1) > 64:
            self.request.session.flash(self._message(u"メールアドレスは64文字以下のものをご使用ください"))
            validated = False
        if not cform.validate() or not birthday:
            self.request.session.flash(self._message(u"購入者情報に入力不備があります"))
            if not birthday:
                cform['birthday'].errors = [_(u'日付が正しくありません')] if self.request.organization.setting.i18n else [u'日付が正しくありません']
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
            memo=cform['memo'].data,
            extra=(cform['extra'].data if 'extra' in cform else None)
            )

        entry = api.get_lot_entry_dict(self.request)
        if entry is None:
            self.request.session.flash(self._message(u"セッションに問題が発生しました。"))
            return self.back_to_form()

        self.request.session['lots.entry.time'] = get_now(self.request)

        if cart_api.is_point_input_required(self.context, self.request):
            return HTTPFound(self.request.route_path('lots.entry.rsp'))

        result = api.prepare1_for_payment(self.request, entry)
        if callable(result):
            return result

        location = urls.entry_confirm(self.request)
        return HTTPFound(location=location)

@view_defaults(route_name='lots.entry.confirm')
class ConfirmLotEntryView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self._message = partial(h._message, request=self.request)

    @lbr_view_config(request_method="GET", renderer=selectable_renderer("confirm.html"))
    def get(self):
        # セッションから表示
        entry = api.get_lot_entry_dict(self.request)
        if entry is None:
            return self.back_to_form()
        if not entry.get('token'):
            self.request.session.flash(self._message(u"セッションに問題が発生しました。"))
            return self.back_to_form()
        # wishesを表示内容にする
        event = self.context.event
        lot = self.context.lot

        payment_delivery_method_pair_id = entry['payment_delivery_method_pair_id']
        payment_delivery_method_pair = PaymentDeliveryMethodPair.query.filter(PaymentDeliveryMethodPair.id==payment_delivery_method_pair_id).one()

        magazines_to_subscribe = get_magazines_to_subscribe(self.context.organization, [entry['shipping_address']['email_1']])

        ks = { }
        organization = self.context.organization
        if organization.setting.enable_word == 1:
            user = cart_api.get_user(self.context.authenticated_user()) # これも読み直し
            if user is not None:
                try:
                    for p in lot.performances:
                        res = cart_api.get_keywords_from_cms(self.request, p.id)
                        for w in res["words"]:
                            # TODO: subscribe状況をセットしてあげても良いが
                            ks[w["id"]] = [ type('', (), { 'id': w["id"], 'label': w["label"] }), False ]
                except Exception as e:
                    logger.warn("Failed to get words info from cms")

        logger.debug('wishes={0}'.format(entry['wishes']))
        wishes = api.build_temporary_wishes(entry['wishes'],
                                            payment_delivery_method_pair=payment_delivery_method_pair,
                                            sales_segment=lot.sales_segment)

        acc = api.get_user_point_account_from_session(self.request)

        for wish in wishes:
            assert wish.performance, type(wish)

        # temporary_entry = api.build_temporary_lot_entry(
        #     lot=lot,
        #     wishes=entry['wishes'],

        raw_extra_form_data = entry.get('extra', [])
        extra_form_data = []
        if raw_extra_form_data is not None:
            extra_form_data = get_extra_form_data_pair_pairs(
                self.context,
                self.request,
                self.context.lot.sales_segment,
                raw_extra_form_data,
                for_='lots',
                mode='entry'
                )
        return dict(event=event,
                    lot=lot,
                    shipping_address=entry['shipping_address'],
                    payment_delivery_method_pair_id=entry['payment_delivery_method_pair_id'],
                    payment_delivery_method_pair=payment_delivery_method_pair,
                    token=entry['token'],
                    wishes=wishes,
                    gender=entry['gender'],
                    birthday=entry['birthday'],
                    memo=entry['memo'],
                    extra_form_data=extra_form_data,
                    mailmagazines_to_subscribe=magazines_to_subscribe,
                    keywords_to_subscribe=ks.values(),
                    accountno=acc.account_number if acc else "",
                    membershipinfo = self.context.membershipinfo,
                    custom_locale_negotiator=custom_locale_negotiator(self.request) if self.request.organization.setting.i18n else ""
                    )

    def back_to_form(self):
        return HTTPFound(location=urls.entry_index(self.request))

    @lbr_view_config(request_method="POST")
    def post(self):
        if 'back' in self.request.params or 'back.x' in self.request.params:
            return self.back_to_form()

        if not h.validate_token(self.request):
            self.request.session.flash(self._message(u"セッションに問題が発生しました。"))
            return self.back_to_form()
        basetime = self.request.session.get('lots.entry.time')
        if basetime is None:
            self.request.session.flash(self._message(u"セッションに問題が発生しました。"))
            return self.back_to_form()

        if basetime + timedelta(minutes=15) < get_now(self.request):
            self.request.session.flash(self._message(u"セッションに問題が発生しました。"))
            return self.back_to_form()


        entry = api.get_lot_entry_dict(self.request)
        if entry is None:
            self.request.session.flash(self._message(u"セッションに問題が発生しました。"))
            return self.back_to_form()

        entry.pop('token')
        entry_no = entry['entry_no']
        shipping_address = entry['shipping_address']
        shipping_address = h.convert_shipping_address(shipping_address)
        user = cart_api.get_or_create_user(self.context.authenticated_user())
        shipping_address.user = user
        wishes = entry['wishes']
        logger.debug('wishes={0}'.format(wishes))

        lot = self.context.lot


        try:
            self.request.session['lots.magazine_ids'] = [long(v) for v in self.request.params.getall('mailmagazine')]
            self.request.session['lots.word_ids'] = [long(v) for v in self.request.params.getall('keyword')]
        except (TypeError, ValueError):
            raise HTTPBadRequest()
        logger.info(repr(self.request.session['lots.magazine_ids']))

        api.prepare2_for_payment(self.request, entry)

        payment_delivery_method_pair_id = entry['payment_delivery_method_pair_id']
        payment_delivery_method_pair = PaymentDeliveryMethodPair.query.filter(PaymentDeliveryMethodPair.id==payment_delivery_method_pair_id).one()

        acc = api.get_user_point_account_from_session(self.request)
        if acc is not None:
            accs = [acc]
        elif self.context.membershipinfo is not None and not self.context.membershipinfo.enable_point_input and user is not None:
            accs = user.user_point_accounts.values()
        else:
            accs = []

        entry = api.entry_lot(
            self.request,
            entry_no=entry_no,
            lot=lot,
            shipping_address=shipping_address,
            wishes=wishes,
            payment_delivery_method_pair=payment_delivery_method_pair,
            user=user,
            gender=entry['gender'],
            birthday=entry['birthday'],
            memo=entry['memo'],
            extra=entry.get('extra', []),
            user_point_accounts=accs
            )
        self.request.session['lots.entry_no'] = entry.entry_no
        api.clear_lot_entry(self.request)
        api.clear_user_point_account_from_session(self.request)

        # extra_form_data = cart_api.load_extra_form_data(self.request)
        # if extra_form_data is not None:
        #    entry.attributes = coerce_extra_form_data(self.request, extra_form_data)
        api.notify_entry_lot(self.request, entry)
        return HTTPFound(location=urls.entry_completion(self.request))


@view_defaults(route_name='lots.entry.completion')
class CompletionLotEntryView(object):
    """ 申し込み完了 """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self._message = partial(h._message, request=self.request)

    @lbr_view_config(request_method="GET", renderer=selectable_renderer("completion.html"))
    def get(self):
        """ 完了画面 """
        if 'lots.entry_no' not in self.request.session:
            return HTTPFound(location=self.request.route_url('lots.entry.index', **self.request.matchdict))
        entry_no = self.request.session.get('lots.entry_no')
        entry = DBSession.query(LotEntry).filter(LotEntry.entry_no==entry_no).one()
        if entry is None:
            self.request.session.flash(self._message(u"セッションに問題が発生しました。"))
            return self.back_to_form()

        cart_api.logout(self.request)

        try:
            api.get_options(self.request, entry.lot.id).dispose()
        except TypeError:
            pass

        user = cart_api.get_or_create_user(self.context.authenticated_user())

        magazine_ids = self.request.session.get('lots.magazine_ids')
        if magazine_ids:
            multi_subscribe(user, entry.shipping_address.emails, magazine_ids)
            try:
                del self.request.session['lots.magazine_ids']
            except:
                pass

        # お気に入り登録
        organization = self.context.organization
        if organization.setting.enable_word == 1:
            word_ids = self.request.session.get('lots.word_ids')
            if word_ids:
                word_subscribe(self.request, user, word_ids)

        # raw_extra_form_data = cart_api.load_extra_form_data(self.request)
        # extra_form_data = None
        # if raw_extra_form_data is not None:
        #     extra_form_data = get_extra_form_data_pair_pairs(
        #         self.context,
        #         self.request,
        #         self.context.sales_segment,
        #         raw_extra_form_data,
        #         for_='lots',
        #         mode='entry'
        #         )

        return dict(
            event=self.context.event,
            lot=self.context.lot,
            sales_segment=self.context.lot.sales_segment,
            entry=entry,
            payment_delivery_method_pair=entry.payment_delivery_method_pair,
            shipping_address=entry.shipping_address,
            wishes=entry.wishes,
            gender=entry.gender,
            birthday=entry.birthday,
            memo=entry.memo,
            custom_locale_negotiator=custom_locale_negotiator(self.request) if self.request.organization.setting.i18n else ""
            )

@view_defaults(route_name='lots.review.index')
class LotReviewView(object):
    """ 申し込み確認 """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self._message = partial(h._message, request=self.request)

    @lbr_view_config(request_method="GET", renderer=selectable_renderer("review_form.html"))
    def get(self):
        """ 申し込み確認照会フォーム """
        jump_maintenance_page_om_for_trouble(self.request.organization)
        form = schemas.ShowLotEntryForm()
        return dict(form=form)

    @lbr_view_config(request_method="POST", renderer=selectable_renderer("review_form.html"))
    def post(self):
        """ 申し込み情報表示"""
        jump_maintenance_page_om_for_trouble(self.request.organization)
        form = schemas.ShowLotEntryForm(formdata=self.request.params)
        try:
            if not form.validate():
                raise ValidationError()
            entry_no = form.entry_no.data
            tel_no = form.tel_no.data
            lot_entry = api.get_entry(self.request, entry_no, tel_no)
            if lot_entry is None or lot_entry.canceled_at:
                form.entry_no.errors.append(self._message(u'{0}または{1}が違います').format(form.entry_no.label.text, form.tel_no.label.text))
                raise ValidationError()
        except ValidationError:
            return dict(form=form)
        # XXX: hack
        jump_infomation_page_om_for_10873(lot_entry)
        return my_render_view_to_response(lot_entry, self.request)

    @lbr_view_config(request_method="POST", renderer=selectable_renderer("review.html"), context=LotEntry)
    def post_validated(self):
        jump_maintenance_page_om_for_trouble(self.request.organization)
        lot_entry = self.context
        api.entry_session(self.request, lot_entry)
        event_id = lot_entry.lot.event.id # いる？
        lot_id = lot_entry.lot.id # いる？
        organization_id = lot_entry.lot.event.organization.id
        user_point_accounts = lot_entry.user_point_accounts
        entry_controller = LotEntryController(self.request)
        entry_controller.load(lot_entry)
        timestamp = datetime.now()
        organization_setting = OrganizationSetting.query \
                                    .filter_by(organization_id=organization_id) \
                                    .first()
        if organization_setting:
            lot_entry_user_withdraw = organization_setting.lot_entry_user_withdraw

        # 当選して、未決済の場合、決済画面に移動可能
        return dict(entry=lot_entry,
            wishes=lot_entry.wishes,
            lot=lot_entry.lot,
            entry_no=lot_entry.entry_no,
            tel_no=self.request.params['tel_no'],
            shipping_address=lot_entry.shipping_address,
            gender=lot_entry.gender,
            birthday=lot_entry.birthday,
            user_point_accounts=user_point_accounts,
            memo=lot_entry.memo,
            entry_controller=entry_controller,
            timestamp=timestamp,
            can_withdraw=lot_entry_user_withdraw and lot_entry.lot.lot_entry_user_withdraw,
            can_withdraw_show=self.context.check_withdraw_show(self.request),
            now=get_now(self.request),
            custom_locale_negotiator=custom_locale_negotiator(self.request) if self.request.organization.setting.i18n else "")


@lbr_view_config(
    context=".exceptions.OutTermException",
    renderer=selectable_renderer("out_term_exception.html")
    )
def out_term_exception(context, request):
    return dict(lot=context.lot)


@lbr_view_config(
    context="altair.app.ticketing.payments.exceptions.PaymentPluginException",
    renderer=selectable_renderer('message.html')
    )
def payment_plugin_exception(context, request):
    _message = partial(h._message, request=request)
    if context.back_url is not None:
        return HTTPFound(location=context.back_url)
    else:
        location = request.context.host_base_url
    return dict(message=Markup(_message(u'決済中にエラーが発生しました。しばらく時間を置いてから<a href="{0}">再度お試しください。</a>').format(location)))


@lbr_notfound_view_config(
    renderer=selectable_renderer('notfound.html'),
    append_slash=True
    )
def notfound(context, request):
    default_msg = u'該当の抽選申込みページは見つかりませんでした'
    display_msg = context.comment or default_msg
    session_clear_url = None
    # session情報のconflictで404なった場合のみクリア用urlを入れる
    if context.detail == u'lots_session_conflict':
        session_clear_url = add_session_clear_query(request.url)
    return dict(display_msg=display_msg, session_clear_url=session_clear_url)


@view_defaults(route_name='lots.entry.logout')
class LogoutView(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @lbr_view_config(request_method="GET", renderer=selectable_renderer("logout.html"))
    def get(self):
        return {}

    @lbr_view_config(request_method="POST")
    def post(self):
        cart_api.logout(self.request)
        if self.context.lot is not None:
            return HTTPFound(self.request.route_url('lots.entry.index', event_id=self.context.lot.event.id, lot_id=self.context.lot.id), headers=self.request.response.headers)
        else:
            return HTTPFound(self.context.host_base_url or "/", headers=self.request.response.headers)


@view_defaults(route_name='lots.entry.rsp', renderer=selectable_renderer("point.html"))
class LotRspView(object):
    """ 申し込み確認 """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @lbr_view_config(request_method="GET")
    def rsp(self):
        lot_asid = self.context.lot_asid
        return self.context.get_rsp(lot_asid)

    @lbr_view_config(request_method="POST")
    def rsp_post(self):
        lot_asid = self.context.lot_asid
        return self.context.post_rsp(lot_asid)

class LotReviewWithdrawView(object):
    """抽選申込取消"""

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.entry = context.entry
        self.organization_id = self.entry.organization_id
        self.error_msg = ""
        self.can_withdraw = False

    @lbr_view_config(route_name='lots.review.withdraw.withdraw',
                     renderer=selectable_renderer("review_withdraw_completion.html"))
    def withdraw(self):
        """申込取消実行"""
        try:
            check_csrf_token(self.request)
        except:
            logger.debug("csrf token error: {0} {1}" . format(self.context.entry.entry_no, self.request.session.get_csrf_token()))
            raise HTTPNotFound()
        if '_csrft_' in self.request.session:
            del self.request.session['_csrft_']
            self.request.session.persist()
        if not self.context.entry:
            raise ValueError()
        try:
            self.context.entry.withdraw(self.request)
            self.can_withdraw = True
            mutil = get_mail_utility(self.request, MailTypeEnum.LotsWithdrawMail)
            mutil.send_mail(self.request, (self.context.entry, None))
        except LotEntryWithdrawException as e:
            self.error_msg = e.message
        return self.build_response_dict()

    @lbr_view_config(route_name='lots.review.withdraw.confirm',
                     renderer=selectable_renderer("review_withdraw_confirm.html"))
    def confirm(self):
        """申込取消確認"""
        try:
            self.context.entry.check_withdraw(self.request)
            self.can_withdraw = True
        except LotEntryWithdrawException as e:
            self.error_msg = e.message
        try:
            check_csrf_token(self.request)
        except:
            logger.debug("csrf token error: {0} {1}" . format(self.context.entry.entry_no, self.request.session.get_csrf_token()))
            raise HTTPNotFound()
        if '_csrft_' in self.request.session:
            del self.request.session['_csrft_']
            self.request.session.persist()
        return self.build_response_dict()

    def build_response_dict(self):
        lot_entry = self.context.entry

        if not lot_entry:
            raise ValueError()

        api.entry_session(self.request, lot_entry)
        entry_controller = LotEntryController(self.request)
        entry_controller.load(lot_entry)
        tel_no = lot_entry.shipping_address.tel_1 or lot_entry.shipping_address.tel_2
        timestamp = datetime.now()
        now = datetime.now()

        return dict(
            entry=lot_entry,
            entry_no=lot_entry.entry_no,
            tel_no=tel_no,
            wishes=lot_entry.wishes,
            lot=lot_entry.lot,
            shipping_address=lot_entry.shipping_address,
            gender=lot_entry.gender,
            birthday=lot_entry.birthday,
            memo=lot_entry.memo,
            entry_controller=entry_controller,
            timestamp=timestamp,
            can_withdraw=self.can_withdraw,
            error_msg=self.error_msg,
            now = now,
        )

