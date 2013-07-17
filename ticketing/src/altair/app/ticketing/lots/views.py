# -*- coding:utf-8 -*-
from datetime import datetime, timedelta
import logging
import operator
#import json

from webob.multidict import MultiDict
from markupsafe import Markup
from pyramid.view import view_config, view_defaults
#from pyramid.view import render_view_to_response
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPBadRequest
from sqlalchemy.orm.exc import NoResultFound

from wtforms.validators import ValidationError
from altair.mobile import mobile_view_config
from altair.pyramid_tz.api import get_timezone

from altair.app.ticketing.models import DBSession
from altair.app.ticketing.core.models import PaymentDeliveryMethodPair
#from altair.app.ticketing.cart import api as cart_api
from altair.app.ticketing.users import api as user_api
from altair.app.ticketing.utils import toutc
from altair.app.ticketing.payments.payment import Payment
from altair.app.ticketing.cart.exceptions import NoCartError
from altair.app.ticketing.mailmags.api import get_magazines_to_subscribe, multi_subscribe

from . import api
from . import helpers as h
from . import schemas
from . import selectable_renderer
from .exceptions import NotElectedException
from .models import (
    #Lot,
    LotEntry,
    #LotEntryWish,
    #LotElectedEntry,
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

    #for v in performance_map.itervalues():
    #    v.sort(lambda a, b: cmp(a['start_on'], b['start_on']))
    for k in performance_map:
        v = performance_map[k]
        performance_map[k] = sorted(v,
                                    key=lambda x: (x['start_on'], x['id']))

    retval = list(performance_map.iteritems())
    #retval.sort(lambda a, b: cmp(a[1][0]['start_on'], b[1][0]['start_on']))
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

@view_config(context=NoResultFound)
def no_results_found(context, request):
    """ 改良が必要。ログに該当のクエリを出したい。 """
    logger.warning(context)    
    return HTTPNotFound()

@view_config(context=NoCartError)
def no_cart_error(context, request):
    logger.warning(context)
    return HTTPNotFound()

@view_defaults(route_name='lots.entry.index', renderer=selectable_renderer("pc/%(membership)s/index.html"), permission="lots")
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
        user = user_api.get_or_create_user(self.context.authenticated_user())
        user_profile = None
        if user is not None:
            user_profile = user.user_profile

        if user_profile is not None:
            formdata = MultiDict(
                last_name=user_profile.last_name,
                last_name_kana=user_profile.last_name_kana,
                first_name=user_profile.first_name,
                first_name_kana=user_profile.first_name_kana,
                tel_1=user_profile.tel_1,
                fax=getattr(user_profile, "fax", None),
                zip=user_profile.zip,
                prefecture=user_profile.prefecture,
                city=user_profile.city,
                address_1=user_profile.address_1,
                address_2=user_profile.address_2,
                email_1=user_profile.email_1,
                email_2=user_profile.email_2
                )
        else:
            formdata = None

        return schemas.ClientForm(formdata=formdata)

    @view_config(request_method="GET")
    def get(self, form=None):
        """

        """
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
        performances = sorted(performances, key=operator.attrgetter('start_on'))

        performance_map = make_performance_map(self.request, performances)

        stocks = lot.stock_types

        performance_id = self.request.params.get('performance')
        selected_performance = None
        if performance_id:
            for p in lot.performances:
                if str(p.id) == performance_id:
                    selected_performance = p
                    break

        # if not stocks:
        #     logger.debug('lot stocks found')
        #     raise HTTPNotFound()


        sales_segment = lot.sales_segment
        payment_delivery_pairs = sales_segment.payment_delivery_method_pairs
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
            payment_delivery_pairs=payment_delivery_pairs,
            posted_values=dict(self.request.POST),
            performance_product_map=performance_product_map,
            stock_types=stock_types, selected_performance=selected_performance,
            payment_delivery_method_pair_id=self.request.params.get('payment_delivery_method_pair_id'),
            lot=lot, performances=performances, performance_map=performance_map, stocks=stocks)

    @view_config(request_method="POST")
    def post(self):
        """ 抽選申し込み作成(一部)
        商品、枚数チェック
        申し込み排他チェック
        - 申し込み回数
        - 申し込み内の公演、席種排他チェック
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
        wishes = h.convert_wishes(self.request.params, lot.limit_wishes)

        validated = True
        email = self.request.params['email_1']
        # 申込回数チェック
        if not lot.check_entry_limit(email):
            self.request.session.flash(u"抽選への申込は{0}回までとなっております。".format(lot.entry_limit))
            validated = False


        # 枚数チェック
        if not wishes:
            self.request.session.flash(u"申し込み内容に入力不備があります")
            validated = False
        elif not h.check_quantities(wishes, lot.upper_limit):
            self.request.session.flash(u"各希望ごとの合計枚数は最大{0}枚までにしてください".format(lot.upper_limit))
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

        entry = self.request.session['lots.entry']
        self.request.session['lots.entry.time'] = datetime.now()
        cart = LotSessionCart(entry, self.request, self.context.lot)

        payment = Payment(cart, self.request)
        self.request.session['payment_confirm_url'] = urls.entry_confirm(self.request)

        result = payment.call_prepare()
        if callable(result):
            return result

        location = urls.entry_confirm(self.request)
        return HTTPFound(location=location)

@view_defaults(route_name='lots.entry.confirm')
class ConfirmLotEntryView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(request_method="GET", renderer=selectable_renderer("pc/%(membership)s/confirm.html"))
    @mobile_view_config(request_method="GET", renderer=selectable_renderer("mobile/%(membership)s/confirm.html"))
    def get(self):
        # セッションから表示
        entry = self.request.session.get('lots.entry')
        if entry is None:
            return self.back_to_form()
        if not entry.get('token'):
            self.request.session.flash(u"セッションに問題が発生しました。")
            return self.back_to_form()
        # wishesを表示内容にする
        event = self.context.event
        lot = self.context.lot

        payment_delivery_method_pair_id = entry['payment_delivery_method_pair_id']
        payment_delivery_method_pair = PaymentDeliveryMethodPair.query.filter(PaymentDeliveryMethodPair.id==payment_delivery_method_pair_id).one()

        DBSession.add(self.context.organization)
        magazines_to_subscribe = get_magazines_to_subscribe(self.context.organization, [entry['shipping_address']['email_1']])

        temporary_entry = api.build_temporary_lot_entry(
            lot=lot,
            wishes=entry['wishes'],
            payment_delivery_method_pair=payment_delivery_method_pair)

        return dict(event=event,
                    lot=lot,
                    shipping_address=entry['shipping_address'],
                    payment_delivery_method_pair_id=entry['payment_delivery_method_pair_id'],
                    payment_delivery_method_pair=payment_delivery_method_pair,
                    token=entry['token'],
                    wishes=temporary_entry.wishes,
                    gender=entry['gender'],
                    birthday=entry['birthday'],
                    memo=entry['memo'],
                    mailmagazines_to_subscribe=magazines_to_subscribe)

    def back_to_form(self):
        return HTTPFound(location=urls.entry_index(self.request))

    @view_config(request_method="POST")
    def post(self):
        if 'back' in self.request.params or 'back.x' in self.request.params:
            return self.back_to_form()

        if not h.validate_token(self.request):
            self.request.session.flash(u"セッションに問題が発生しました。")
            return self.back_to_form()
        basetime = self.request.session.get('lots.entry.time')
        if basetime is None:
            self.request.session.flash(u"セッションに問題が発生しました。")
            return self.back_to_form()

        if basetime + timedelta(minutes=15) < datetime.now():
            self.request.session.flash(u"セッションに問題が発生しました。")
            return self.back_to_form()


        entry = self.request.session['lots.entry']
        entry.pop('token')
        entry_no = entry['entry_no']
        shipping_address = entry['shipping_address']
        shipping_address = h.convert_shipping_address(shipping_address)
        wishes = entry['wishes']

        lot = self.context.lot

        try:
            self.request.session['lots.magazine_ids'] = [long(v) for v in self.request.params.getall('mailmagazine')]
        except (TypeError, ValueError):
            raise HTTPBadRequest()
        logger.info(repr(self.request.session['lots.magazine_ids']))

        payment_delivery_method_pair_id = entry['payment_delivery_method_pair_id']
        payment_delivery_method_pair = PaymentDeliveryMethodPair.query.filter(PaymentDeliveryMethodPair.id==payment_delivery_method_pair_id).one()

        user = api.get_entry_user(self.request)

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
            memo=entry['memo']
            )
        self.request.session['lots.entry_no'] = entry.entry_no


        try:
            api.notify_entry_lot(self.request, entry)
        except Exception as e:
            logger.warning('error orccured during sending mail. \n{0}'.format(e))


        return HTTPFound(location=urls.entry_completion(self.request))

@view_defaults(route_name='lots.entry.completion')
class CompletionLotEntryView(object):
    """ 申し込み完了 """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(request_method="GET", renderer=selectable_renderer("pc/%(membership)s/completion.html"))
    @mobile_view_config(request_method="GET", renderer=selectable_renderer("mobile/%(membership)s/completion.html"))
    def get(self):
        """ 完了画面 """
        if 'lots.entry_no' not in self.request.session:
            return HTTPFound(location=self.request.route_url('lots.entry.index', **self.request.matchdict))
        entry_no = self.request.session.pop('lots.entry_no')
        entry = DBSession.query(LotEntry).filter(LotEntry.entry_no==entry_no).one()


        try:
            api.get_options(self.request, entry.lot.id).dispose()
        except TypeError:
            pass

        magazine_ids = self.request.session.get('lots.magazine_ids')
        if magazine_ids:
            user = user_api.get_or_create_user(self.context.authenticated_user())
            multi_subscribe(user, entry.shipping_address.emails, magazine_ids)
            self.request.session['lots.magazine_ids'] = None
            self.request.session.persist() # XXX: 完全に念のため

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
            memo=entry.memo
            )

@view_defaults(route_name='lots.review.index')
class LotReviewView(object):
    """ 申し込み確認 """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(request_method="GET", renderer=selectable_renderer("pc/%(membership)s/review_form.html"))
    @mobile_view_config(request_method="GET", renderer=selectable_renderer("mobile/%(membership)s/review_form.html"))
    def get(self):
        """ 申し込み確認照会フォーム """
        form = schemas.ShowLotEntryForm()
        return dict(form=form)

    @view_config(request_method="POST", renderer=selectable_renderer("pc/%(membership)s/review_form.html"))
    @mobile_view_config(request_method="POST", renderer=selectable_renderer("mobile/%(membership)s/review_form.html"))
    def post(self):
        """ 申し込み情報表示"""
        form = schemas.ShowLotEntryForm(formdata=self.request.params)
        try:
            if not form.validate():
                raise ValidationError()
            entry_no = form.entry_no.data
            tel_no = form.tel_no.data
            lot_entry = api.get_entry(self.request, entry_no, tel_no)
            if lot_entry is None:
                form.entry_no.errors.append(u'%sまたは%sが違います' % (form.entry_no.label.text, form.tel_no.label.text))
                raise ValidationError()
        except ValidationError:
            return dict(form=form)
        # XXX: hack
        return my_render_view_to_response(lot_entry, self.request)

    @view_config(request_method="POST", renderer=selectable_renderer("pc/%(membership)s/review.html"), context=LotEntry)
    @mobile_view_config(request_method="POST", renderer=selectable_renderer("mobile/%(membership)s/review.html"), context=LotEntry)
    def post_validated(self):
        lot_entry = self.context
        api.entry_session(self.request, lot_entry)
        event_id = lot_entry.lot.event.id
        lot_id = lot_entry.lot.id
        # 当選して、未決済の場合、決済画面に移動可能
        return dict(entry=lot_entry,
            wishes=lot_entry.wishes,
            lot=lot_entry.lot,
            shipping_address=lot_entry.shipping_address,
            gender=lot_entry.gender,
            birthday=lot_entry.birthday,
            memo=lot_entry.memo) 

@view_config(context=".exceptions.OutTermException",
             renderer=selectable_renderer("pc/%(membership)s/out_term_exception.html"))
@mobile_view_config(context=".exceptions.OutTermException",
             renderer=selectable_renderer("mobile/%(membership)s/out_term_exception.html"))
def out_term_exception(context, request):
    return dict(lot_name=context.lot_name,
                from_=context.from_,
                to_=context.to_,
                )




@view_config(context="altair.app.ticketing.payments.exceptions.PaymentPluginException", 
             renderer=selectable_renderer('pc/%(membership)s/message.html'))
@mobile_view_config(context="altair.app.ticketing.payments.exceptions.PaymentPluginException", 
             renderer=selectable_renderer('mobile/%(membership)s/error.html'))
def payment_plugin_exception(context, request):
    if context.back_url is not None:
        return HTTPFound(location=context.back_url)
    else:
        location = request.context.host_base_url
    return dict(message=Markup(u'決済中にエラーが発生しました。しばらく時間を置いてから<a href="%s">再度お試しください。</a>' % location))
