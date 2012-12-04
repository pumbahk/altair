# -*- coding:utf-8 -*-
import logging
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
import ticketing.cart.api as cart_api
from ticketing.models import DBSession
from ticketing.core.models import PaymentDeliveryMethodPair
from sqlalchemy.orm.exc import NoResultFound
from . import apis
from . import helpers as h
from . import schemas
from .exceptions import NotElectedException
from pyramid.httpexceptions import HTTPNotFound
from uuid import uuid4
from ticketing.payments.payment import Payment

from .models import (
    LotEntry,
    LotEntryWish,
    LotElectedEntry,
)

logger = logging.getLogger(__name__)

@view_config(context=NoResultFound)
def no_results_found(context, request):
    """ 改良が必要。ログに該当のクエリを出したい。 """
    logger.warning(context)    
    return HTTPNotFound()

@view_defaults(route_name='lots.entry.index', renderer="index.html")
class EntryLotView(object):
    """
    申し込み画面
    商品 x 枚数 を入力
    購入者情報を入力
    決済方法を選択
    """

    def __init__(self, request):
        self.request = request

    def _get_lot_info(self):
        event = apis.get_event(self.request)
        member_group = apis.get_member_group(self.request)
        sales_segment = apis.get_sales_segment(self.request, event, member_group)
        lot_id = self.request.matchdict.get('lot_id')
        return apis.get_lot(self.request, event, sales_segment, lot_id)

    @view_config(request_method="GET")
    def get(self, form=None):
        """

        """
        if form is None:
            form = schemas.ClientForm()

        lot, performances, stocks = self._get_lot_info()
        event = lot.event
        sales_segment = lot.sales_segment
        products = apis.get_products(self.request, sales_segment)
        payment_delivery_pairs = sales_segment.payment_delivery_method_pairs
        return dict(form=form, event=event, sales_segment=sales_segment,
            payment_delivery_pairs=payment_delivery_pairs,
            products=products,
            payment_delivery_method_pair_id=self.request.params.get('payment_delivery_method_pair_id'),
            lot=lot, performances=performances, stocks=stocks)

    @view_config(request_method="POST")
    def post(self):
        """ 抽選申し込み作成(一部)
        商品、枚数チェック
        申し込み排他チェック
        - 申し込み回数
        - 申し込み内の公演、席種排他チェック
        """
        lot, performances, stocks = self._get_lot_info()
        cform = schemas.ClientForm(formdata=self.request.params)
        sales_segment = lot.sales_segment
        payment_delivery_pairs = sales_segment.payment_delivery_method_pairs
        payment_delivery_method_pair_id = self.request.params.get('payment_delivery_method_pair_id')
        wishes = h.convert_wishes(self.request.params, lot.limit_wishes)
        
        # 希望選択
        if not wishes or not lot.validate_entry(self.request.params):
            self.request.session.flash(u"申し込み内容に入力不備があります")
            return self.get(form=cform)
        

        # 決済配送方法選択
        if payment_delivery_method_pair_id not in [str(m.id) for m in payment_delivery_pairs]:
            self.request.session.flash(u"お支払お引き取り方法を選択してください")
            return self.get(form=cform)

        # 購入者情報
        if not cform.validate():
            self.request.session.flash(u"購入者情報に入力不備があります")
            return self.get(form=cform)


        shipping_address = cform.get_validated_address_data()
        self.request.session['lots.entry'] = dict(
            token=uuid4().hex,
            wishes=wishes,
            payment_delivery_method_pair_id=payment_delivery_method_pair_id,
            shipping_address=shipping_address)
        location = self.request.route_url('lots.entry.confirm', **self.request.matchdict)
        return HTTPFound(location=location)

@view_defaults(route_name='lots.entry.confirm', renderer="confirm.html")
class ConfirmLotEntryView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(request_method="GET")
    def get(self):
        # セッションから表示
        entry = self.request.session.get('lots.entry')
        if entry is None:
            return self.back_to_form()
        # wishesを表示内容にする

        payment_delivery_method_pair_id = entry['payment_delivery_method_pair_id']
        payment_delivery_method_pair = PaymentDeliveryMethodPair.query.filter(PaymentDeliveryMethodPair.id==payment_delivery_method_pair_id).one()
        return dict(shipping_address=entry['shipping_address'],
            payment_delivery_method_pair_id=entry['payment_delivery_method_pair_id'],
            payment_delivery_method_pair=payment_delivery_method_pair,
            token=entry['token'],
            wishes=h.add_wished_product_names(entry['wishes']))

    def back_to_form(self):
        return HTTPFound(location=self.request.route_url('lots.entry.index',
            event_id=self.request.matchdict.get('event_id'),
            lot_id=self.request.matchdict.get('lot_id')))

    def get_lot(self):
        event = apis.get_event(self.request)
        member_group = apis.get_member_group(self.request)
        sales_segment = apis.get_sales_segment(self.request, event, member_group)
        lot_id = self.request.matchdict.get('lot_id')
        return apis.get_lot(self.request, event, sales_segment, lot_id)

    @view_config(request_method="POST")
    def post(self):
        if 'back' in self.request.params:
            return self.back_to_form()

        if not h.validate_token(self.request):
            self.request.session.flash(u"セッションに問題が発生しました。")
            return self.back_to_form()
        entry = self.request.session['lots.entry']
        shipping_address = entry['shipping_address']
        shipping_address = h.convert_shipping_address(shipping_address)
        wishes = entry['wishes']

        lot, performances, stock_types = self.get_lot()
        if not lot.validate_entry(self.request.params):
            return HTTPFound('lots.entry.index')
        payment_delivery_method_pair_id = entry['payment_delivery_method_pair_id']
        payment_delivery_method_pair = PaymentDeliveryMethodPair.query.filter(PaymentDeliveryMethodPair.id==payment_delivery_method_pair_id).one()

        user = None
        entry = apis.entry_lot(self.request, lot, shipping_address, wishes, payment_delivery_method_pair, user)
        self.request.session['lots.entry_no'] = entry.entry_no
        return HTTPFound(self.request.route_url('lots.entry.completion', **self.request.matchdict))

@view_defaults(route_name='lots.entry.completion', renderer="completion.html")
class CompletionLotEntryView(object):
    """ 申し込み完了 """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(request_method="GET")
    def get(self):
        """ 完了画面 """
        entry_no = self.request.session['lots.entry_no']
        entry = DBSession.query(LotEntry).filter(LotEntry.entry_no==entry_no).one()
        return dict(entry=entry)

@view_defaults(route_name='lots.review.index')
class LotReviewView(object):
    """ 申し込み確認 """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(request_method="GET", renderer="review_form.html")
    def get(self):
        """ 申し込み確認照会フォーム """
        form = schemas.ShowLotEntryForm()
        return dict(form=form)

    @view_config(request_method="POST", renderer="review.html")
    def post(self):
        """ 申し込み情報表示"""
        form = schemas.ShowLotEntryForm(formdata=self.request.params)
        if not form.validate():
            self.request.override_renderer = "review_form.html"
            return dict(form=form)
        entry_no = form["entry_no"].data
        tel_no = form["tel_no"].data
        lot_entry = apis.get_entry(self.request, entry_no, tel_no)
        if lot_entry is None:
            self.request.override_renderer = "review_form.html"
            return dict(form=form)

        apis.entry_session(self.request, lot_entry)
        event_id = lot_entry.lot.event.id
        lot_id = lot_entry.lot.id
        # 当選して、未決済の場合、決済画面に移動可能
        return dict(entry=lot_entry,
            is_elected=lot_entry.is_elected,
            is_rejected=lot_entry.is_rejected,
            is_ordered=lot_entry.is_ordered,
            payment_url=self.request.route_url('lots.payment.index', event_id=event_id, lot_id=lot_id) if lot_entry.is_elected else None) 

@view_defaults(route_name='lots.payment.index', renderer='index_2.html')
class PaymentView(object):
    """ [当選者のみ]
    支払方法選択
    セッションに申し込み者の情報を持つ
    """
    

    def __init__(self, request):
        self.request = request

    @view_config(request_method="GET")
    def show_form(self):
        """
        """
        lot_entry = apis.entry_session(self.request)
        if lot_entry is None:
            location = self.request.route_url('lots.review.index')
            return HTTPFound(location)

        # この申し込みは妥当か？
        if not lot_entry.is_elected:
            return # Forbidden? NotFound?

        lot = apis.get_requested_lot(self.request)
        payment_delivery_method_pairs = lot.sales_segment.payment_delivery_method_pairs
        # 当選情報
        elected = DBSession.query(LotElectedEntry).filter(
            LotElectedEntry.lot_entry_id==lot_entry.id
        ).filter(
            LotElectedEntry.lot_entry_id==LotEntryWish.lot_entry_id
        ).filter(
            LotElectedEntry.lot_entry_wish_id==LotEntryWish.id
        ).first()
        if elected is None:
            return # NotFound?
        shipping_address = lot_entry.shipping_address
        form_data = h.shipping_address_form_data(shipping_address)
        form = schemas.ClientForm(form_data)
        return dict(form=form, lot=lot, elected=elected, lot_entry=lot_entry, 
            payment_delivery_method_pair_id=lot_entry.payment_delivery_method_pair_id,
            payment_delivery_pairs=payment_delivery_method_pairs)

    @view_config(request_method="POST")
    def submit(self):
        """
        決済
        """

        event_id = self.request.matchdict['event_id']
        lot_entry = apis.entry_session(self.request)
        if lot_entry is None:
            raise HTTPNotFound

        if not lot_entry.is_elected:
            raise NotElectedException
        cart = apis.create_cart(self.request, lot_entry)
        DBSession.add(cart)
        DBSession.flush()
        cart_api.set_cart(self.request, cart)

        location = self.request.route_url('lots.payment.confirm', 
            event_id=event_id,
            lot_id=lot_entry.lot.id,
            entry_no=lot_entry.entry_no)
        return HTTPFound(location)

@view_defaults(route_name='lots.payment.confirm', renderer='confirm_2.html')
class PaymentConfirm(object):
    def __init__(self, request):
        self.request = request
    
    @view_config(request_method="GET")
    def get(self):
        """
        """
        event_id = self.request.matchdict['event_id']
        lot_entry = apis.entry_session(self.request)
        if lot_entry is None:
            raise HTTPNotFound

        if not lot_entry.is_elected:
            raise NotElectedException
        cart = cart_api.get_cart(self.request)
        return dict(cart=cart)

    @view_config(request_method="POST", renderer="json")
    def post(self):
        lot_entry = apis.entry_session(self.request)
        if lot_entry is None:
            raise HTTPNotFound

        if not lot_entry.is_elected:
            raise NotElectedException
        if not cart_api.has_cart(self.request):
            raise HTTPNotFound()

        cart = cart_api.get_cart(self.request)
        if not cart.is_valid():
            raise HTTPNotFound()

        payment = Payment(cart, self.request)
        order = payment.call_payment()
        logger.debug("order_no = {0}".format(order.order_no))
        cart_api.remove_cart(self.request)
        lot_entry = apis.entry_session(self.request)
        lot_entry.order = order
        return dict(order_no=order.order_no)

class PaymentCompleted(object):
    """ [当選者のみ]
    """
    
    def __init__(self, request):
        self.request = request

    def __call__(self):
        """ 完了画面 (表示のみ)
        """
        return dict()
