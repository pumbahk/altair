# -*- coding:utf-8 -*-
from datetime import datetime
import logging
import operator
import json

from pyramid.view import view_config, view_defaults
#from pyramid.view import render_view_to_response
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPBadRequest
from sqlalchemy.orm.exc import NoResultFound

from wtforms.validators import ValidationError
from altair.mobile import mobile_view_config
from altair.pyramid_tz.api import get_timezone

from ticketing.models import DBSession
from ticketing.core.models import PaymentDeliveryMethodPair
from ticketing.cart import api as cart_api
from ticketing.utils import toutc
from ticketing.payments.payment import Payment
from ticketing.cart.exceptions import NoCartError

from . import api
from . import helpers as h
from . import schemas
from . import selectable_renderer
from .exceptions import NotElectedException
from .models import (
    #Lot,
    LotEntry,
    LotEntryWish,
    LotElectedEntry,
)
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

    for v in performance_map.itervalues():
        v.sort(lambda a, b: cmp(a['start_on'], b['start_on']))

    retval = list(performance_map.iteritems())
    retval.sort(lambda a, b: cmp(a[1][0]['start_on'], b[1][0]['start_on']))

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

@view_defaults(route_name='lots.entry.index', renderer=selectable_renderer("pc/%(membership)s/index.html"))
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

    def _create_performance_product_map(self, products):
        performance_product_map = {}
        for product in products:
            performance = product.performance
            products = performance_product_map.get(performance.id, [])
            products.append(dict(
                id=product.id,
                name=product.name,
                display_order=product.display_order,
                stock_type_id=product.seat_stock_type_id
            ))
            performance_product_map[performance.id] = products

        key_func = operator.itemgetter('display_order', 'id')
        for p in performance_product_map.values():
            p.sort(key=key_func)
        return performance_product_map

    @view_config(request_method="GET")
    def get(self, form=None):
        """

        """
        if form is None:
            form = schemas.ClientForm()

        event = self.context.event
        lot = self.context.lot

        if not lot:
            logger.debug('lot not not found')
            raise HTTPNotFound()

        performances = lot.performances
        if not performances:
            logger.debug('lot performances not found')
            raise HTTPNotFound()

        performance_map = make_performance_map(self.request, performances)

        stocks = lot.stock_types

        # if not stocks:
        #     logger.debug('lot stocks found')
        #     raise HTTPNotFound()

        sales_segment = lot.sales_segment
        payment_delivery_pairs = sales_segment.payment_delivery_method_pairs
        performance_product_map = self._create_performance_product_map(sales_segment.products)
        stock_types = sorted(set((product.seat_stock_type_id, product.seat_stock_type.name, product.seat_stock_type.display_order) for product in sales_segment.products), lambda a, b: cmp(a[2], b[2]))

        return dict(form=form, event=event, sales_segment=sales_segment,
            payment_delivery_pairs=payment_delivery_pairs,
            posted_values=dict(self.request.POST),
            performance_product_map=performance_product_map,
            stock_types=stock_types,
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
        
        # 希望選択
        if not wishes or not lot.validate_entry(self.request.params):
            self.request.session.flash(u"申し込み内容に入力不備があります")
            return self.get(form=cform)
        

        # 決済・引取方法選択
        if payment_delivery_method_pair_id not in [str(m.id) for m in payment_delivery_pairs]:
            self.request.session.flash(u"お支払お引き取り方法を選択してください")
            return self.get(form=cform)

        # 購入者情報
        if not cform.validate():
            self.request.session.flash(u"購入者情報に入力不備があります")
            return self.get(form=cform)


        shipping_address_dict = cform.get_validated_address_data()
        api.new_lot_entry(
            self.request,
            wishes=wishes,
            payment_delivery_method_pair_id=payment_delivery_method_pair_id,
            shipping_address_dict=shipping_address_dict,
            gender=cform['sex'].data,
            birthday=datetime(int(cform['year'].data),
                              int(cform['month'].data),
                              int(cform['day'].data)),
            memo=cform['memo'].data)

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
        # wishesを表示内容にする
        event = self.context.event
        lot = self.context.lot

        payment_delivery_method_pair_id = entry['payment_delivery_method_pair_id']
        payment_delivery_method_pair = PaymentDeliveryMethodPair.query.filter(PaymentDeliveryMethodPair.id==payment_delivery_method_pair_id).one()
        return dict(event=event,
                    lot=lot,
                    shipping_address=entry['shipping_address'],
                    payment_delivery_method_pair_id=entry['payment_delivery_method_pair_id'],
                    payment_delivery_method_pair=payment_delivery_method_pair,
                    token=entry['token'],
                    wishes=h.add_wished_product_names(entry['wishes']),
                    gender=entry['gender'],
                    birthday=entry['birthday'],
                    memo=entry['memo'])

    def back_to_form(self):
        return HTTPFound(location=urls.entry_index(self.request))

    @view_config(request_method="POST")
    def post(self):
        if 'back' in self.request.params or 'back.x' in self.request.params:
            return self.back_to_form()

        if not h.validate_token(self.request):
            self.request.session.flash(u"セッションに問題が発生しました。")
            return self.back_to_form()

        entry = self.request.session['lots.entry']
        shipping_address = entry['shipping_address']
        shipping_address = h.convert_shipping_address(shipping_address)
        wishes = entry['wishes']

        lot = self.context.lot

        if not lot.validate_entry(self.request.params):
            return HTTPFound('lots.entry.index')
        payment_delivery_method_pair_id = entry['payment_delivery_method_pair_id']
        payment_delivery_method_pair = PaymentDeliveryMethodPair.query.filter(PaymentDeliveryMethodPair.id==payment_delivery_method_pair_id).one()

        user = api.get_entry_user(self.request)

        entry = api.entry_lot(self.request, lot, shipping_address, wishes, payment_delivery_method_pair, user,
                              entry['gender'], entry['birthday'], entry['memo'])
        self.request.session['lots.entry_no'] = entry.entry_no
        api.notify_entry_lot(self.request, entry)

        cart = api.get_entry_cart(self.request, entry)

        payment = Payment(cart, self.request)
        self.request.session['payment_confirm_url'] = urls.entry_completion(self.request)

        result = payment.call_prepare()
        if callable(result):
            return result


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
        entry_no = self.request.session['lots.entry_no']
        entry = DBSession.query(LotEntry).filter(LotEntry.entry_no==entry_no).one()
        try:
            api.get_options(self.request, lot.id).dispose()
        except TypeError:
            pass

        return dict(event=self.context.event, lot=self.context.lot, sales_segment=self.context.lot.sales_segment, entry=entry)

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
            lot=lot_entry.lot,
            shipping_address=lot_entry.shipping_address,
            gender=lot_entry.gender,
            birthday=lot_entry.birthday,
            memo=lot_entry.memo,
            payment_url=self.request.route_url('lots.payment.index', event_id=event_id, lot_id=lot_id) if lot_entry.is_elected else None) 

# @view_defaults(route_name='lots.payment.index')
# class PaymentView(object):
#     """ [当選者のみ]
#     支払方法選択
#     セッションに申し込み者の情報を持つ
#     """
    

#     def __init__(self, context, request):
#         self.context = context
#         self.request = request

#     @view_config(request_method="GET", renderer=selectable_renderer("pc/%(membership)s/index_2.html"))
#     @mobile_view_config(request_method="GET", renderer=selectable_renderer("mobile/%(membership)s/index_2.html"))
#     def show_form(self):
#         """
#         """
#         lot_entry = api.entry_session(self.request)
#         if lot_entry is None:
#             location = self.request.route_url('lots.review.index')
#             return HTTPFound(location)

#         # この申し込みは妥当か？
#         if not lot_entry.is_elected:
#             # 通常のフローでは到達しない → 400
#             raise HTTPBadRequest()

#         lot = api.get_requested_lot(self.request)
#         payment_delivery_method_pairs = lot.sales_segment.payment_delivery_method_pairs
#         # 当選情報
#         elected = DBSession.query(LotElectedEntry).filter(
#             LotElectedEntry.lot_entry_id==lot_entry.id
#         ).filter(
#             LotElectedEntry.lot_entry_id==LotEntryWish.lot_entry_id
#         ).filter(
#             LotElectedEntry.lot_entry_wish_id==LotEntryWish.id
#         ).first()
#         if elected is None:
#             # 通常のフローでは到達しない → 400
#             raise HTTPBadRequest()
#         shipping_address = lot_entry.shipping_address
#         form_data = h.shipping_address_form_data(shipping_address, lot_entry.gender)
#         form = schemas.ClientForm(form_data)
#         wish=elected.lot_entry_wish
#         payment_delivery_method_pair=lot_entry.payment_delivery_method_pair
#         total_amount = sum([wp.product.price * wp.quantity for wp in wish.products]) + payment_delivery_method_pair.transaction_fee + payment_delivery_method_pair.delivery_fee + payment_delivery_method_pair.system_fee

#         return dict(form=form, lot=lot, elected=elected, wish=wish, lot_entry=lot_entry, 
#             total_amount=total_amount,
#             performance=elected.lot_entry_wish.performance,
#             payment_delivery_method_pair_id=lot_entry.payment_delivery_method_pair_id,
#             payment_delivery_method_pair=payment_delivery_method_pair,
#             payment_delivery_pairs=payment_delivery_method_pairs)

#     @view_config(request_method="POST")
#     def submit(self):
#         """
#         決済
#         """

#         event_id = self.context.lot
#         lot_entry = api.entry_session(self.request)
#         if lot_entry is None:
#             raise HTTPNotFound

#         if not lot_entry.is_elected:
#             raise NotElectedException

#         lot = lot_entry.lot
#         cart = api.create_cart(self.request, lot_entry)
#         DBSession.add(cart)
#         DBSession.flush()
#         cart_api.set_cart(self.request, cart)
#         client_name = self.request.params.get('last_name', '') + self.request.params.get('first_name', '')

#         cart_api.new_order_session(
#             self.request,
#             client_name=client_name,
#             payment_delivery_method_pair_id=cart.payment_delivery_pair.id,
#             email_1=cart.shipping_address.email_1,
#         )


#         self.request.session['payment_confirm_url'] = self.request.route_url('lots.payment.confirm', event_id=lot.event_id, lot_id=lot.id)
#         payment = Payment(cart, self.request)
#         result = payment.call_prepare()
#         if callable(result):
#             return result

#         location = self.request.route_url('lots.payment.confirm', 
#             event_id=event_id,
#             lot_id=lot_entry.lot.id,
#             entry_no=lot_entry.entry_no)
#         return HTTPFound(location)

# @view_defaults(route_name='lots.payment.confirm')
# class PaymentConfirm(object):
#     def __init__(self, request):
#         self.request = request
    
#     @view_config(request_method="GET", renderer=selectable_renderer("pc/%(membership)s/confirm_2.html"))
#     @mobile_view_config(request_method="GET", renderer=selectable_renderer("mobile/%(membership)s/confirm_2.html"))
#     def get(self):
#         """
#         """
#         lot_entry = api.entry_session(self.request)
#         if lot_entry is None:
#             raise HTTPNotFound

#         if not lot_entry.is_elected:
#             raise NotElectedException
#         elected = lot_entry.lot_elected_entries[0]
#         cart = cart_api.get_cart(self.request)
#         return dict(
#             lot_entry=lot_entry,
#             lot=lot_entry.lot,
#             elected=elected,
#             performance=elected.lot_entry_wish.performance,
#             cart=cart,
#             payment_delivery_method_pair=cart.payment_delivery_pair,
#             shipping_address=cart.shipping_address,
#             total_amount=cart.total_amount
#             )

#     @view_config(request_method="POST")
#     def post(self):
#         lot_entry = api.entry_session(self.request)
#         if lot_entry is None:
#             raise HTTPNotFound

#         if not lot_entry.is_elected:
#             raise NotElectedException
#         cart = cart_api.get_cart_safe(self.request)
#         if not cart.is_valid():
#             raise HTTPNotFound()

#         payment = Payment(cart, self.request)
#         order = payment.call_payment()
#         logger.debug("order_no = {0}".format(order.order_no))
#         cart_api.remove_cart(self.request)
#         lot_entry = api.entry_session(self.request)
#         lot_entry.order = order
#         return HTTPFound(location=urls.payment_completion(self.request))

# @view_defaults(route_name='lots.payment.completion')
# class PaymentCompleted(object):
#     """ [当選者のみ]
#     """
    
#     def __init__(self, request):
#         self.request = request

#     @view_config(request_method="GET", renderer=selectable_renderer("pc/%(membership)s/completion_2.html"))
#     @mobile_view_config(request_method="GET", renderer=selectable_renderer("mobile/%(membership)s/completion_2.html"))
#     def __call__(self):
#         """ 完了画面 (表示のみ)
#         """
#         lot_entry = api.entry_session(self.request)
#         if lot_entry is None:
#             raise HTTPNotFound

#         order = lot_entry.order
#         if not order:
#             raise HTTPNotFound()

#         elected = lot_entry.lot_elected_entries[0]
#         return dict(
#             order=order,
#             entry=lot_entry,
#             elected=elected,
#             performance=elected.lot_entry_wish.performance,
#             lot=lot_entry.lot,
#             payment_delivery_method_pair=order.payment_delivery_pair,
#             shipping_address=order.shipping_address,
#             total_amount=order.total_amount
#             )
