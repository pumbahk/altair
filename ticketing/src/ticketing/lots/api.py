# -*- coding:utf-8 -*-

"""

ユーザー用

- 抽選取得
- 抽選申し込み
- 抽選申し込み履歴

管理用

- 抽選申し込み状況表示

- 抽選申し込みエクスポート
- 抽選申し込みインポート
- 抽選状況表示
- 抽選確定

抽選確定処理の内部

- 在庫処理
- 注文受け

以下の二種類の販売区分を区別して使う
- 抽選の決済のための販売区分
- 公演ごとの券種のための販売区分

同じ販売区分グループだと楽

"""

import transaction
from datetime import datetime
from uuid import uuid4
from sqlalchemy import sql
from pyramid.interfaces import IRequest
import ticketing.cart.api as cart_api
from ticketing.utils import sensible_alnum_encode
from ticketing.rakuten_auth.api import authenticated_user
from ticketing.core import api as core_api
from ticketing.core.models import (
    Event,
    SalesSegment,
    ShippingAddress,
    DBSession,
)

from ticketing.users.models import (
    MemberGroup_SalesSegment,
    MemberGroup,
    SexEnum,
)
from ticketing.cart.models import (
    Cart,
)

from .models import (
    Lot,
    LotEntry,
    LotEntryWish,
    LotEntryProduct,
    LotElectedEntry,
    LotRejectedEntry,
    LotElectWork,
)

from . import sendmail
from .events import LotEntriedEvent
from .interfaces import IElecting
from .adapters import LotEntryCart

def get_event(request):
    event_id = request.matchdict['event_id']
    return Event.query.filter(Event.id==event_id).one()

def get_member_group(request):
    user = authenticated_user(request)
    if user is None:
        return None
    member_group_name = user.get('membergroup')
    if member_group_name is None:
        return None
    # TODO: membershipの条件
    return MemberGroup.query.filter(MemberGroup.name==member_group_name).one()

def get_sales_segment(request, event, membergroup):
    # TODO: membergroup が Noneであるときにguestとしてよいか検討 guest membergroupを作らなくてもよい？
    if membergroup is None:
        return SalesSegment.query.filter(
            SalesSegment.event_id==event.id
        ).filter(
            MemberGroup_SalesSegment.c.sales_segment_group_id==SalesSegment.id
        ).filter(
            MemberGroup_SalesSegment.c.membergroup_id==MemberGroup.id
        ).filter(
            MemberGroup.is_guest==True
        ).one()
    else:
        return SalesSegment.query.filter(
            SalesSegment.event_id==event.id
        ).filter(
            MemberGroup_SalesSegment.c.sales_segment_group_id==SalesSegment.id
        ).filter(
            MemberGroup_SalesSegment.c.membergroup_id==membergroup.id
        ).one()

def get_requested_lot(request):
    lot_id = request.matchdict.get('lot_id')
    return Lot.query.filter(Lot.id==lot_id).one()


def get_entry_cart(request, entry=None):
    if entry is None:
        entry_id = request.session['altair.lots.entry_id']
        entry = LotEntry.query.filter(LotEntry.id==entry_id).one()
    return LotEntryCart(entry)

def build_lot_entry_wish(wish_order, wish_rec):
    performance_id = long(wish_rec["performance_id"])
    wish = LotEntryWish(wish_order=wish_order, performance_id=performance_id)
    for wished_product_rec in wish_rec["wished_products"]:
        if wished_product_rec['quantity'] > 0:
            product = LotEntryProduct(
                quantity=wished_product_rec["quantity"],
                product_id=wished_product_rec["product_id"]
                )
            wish.products.append(product)
    return wish

def build_lot_entry(lot, wishes, payment_delivery_method_pair, membergroup=None, shipping_address=None, user=None, gender=None, birthday=None, memo=None):
    entry = LotEntry(
        lot=lot,
        shipping_address=shipping_address,
        membergroup=membergroup,
        payment_delivery_method_pair=payment_delivery_method_pair,
        gender=gender,
        birthday=birthday,
        memo=memo)
    for i, wish_rec in enumerate(wishes):
        entry.wishes.append(build_lot_entry_wish(i, wish_rec))
    return entry

def build_temporary_lot_entry(*args, **kwargs):
    entry = build_lot_entry(*args, **kwargs)
    DBSession.expunge(entry)
    return entry

def entry_lot(request, lot, shipping_address, wishes, payment_delivery_method_pair, user, gender, birthday, memo):
    """
    wishes
    {product_id, quantity} の希望順リスト
    :param user: ゲストの場合は None
    """
    entry = build_lot_entry(
        lot=lot,
        wishes=wishes,
        membergroup=get_member_group(request),
        payment_delivery_method_pair=payment_delivery_method_pair,
        shipping_address=shipping_address,
        user=user,
        gender=gender,
        birthday=birthday,
        memo=memo
        )

    DBSession.add(entry)
    DBSession.flush()
    entry.entry_no = generate_entry_no(request, entry)
    for wish in entry.wishes:
        wish.entry_wish_no = "{0}-{1}".format(entry.entry_no, wish.wish_order)
    request.session['altair.lots.entry_id'] = entry.id
    return entry

def get_entry(request, entry_no, tel_no):
    return LotEntry.query.filter(
        LotEntry.entry_no==entry_no,
    ).filter(
        sql.or_(ShippingAddress.tel_1==tel_no, 
            ShippingAddress.tel_2==tel_no)
    ).filter(
        ShippingAddress.id==LotEntry.shipping_address_id
    ).first()


def generate_entry_no(request, lot_entry):
    """ 引き替え用の抽選申し込み番号生成
    TODO:  ticketing.core.api.get_next_order_no を使う
    """
    base_id = core_api.get_next_order_no()
    organization_code = lot_entry.lot.event.organization.code
    return organization_code + sensible_alnum_encode(base_id).zfill(10)


def get_lot_entries_iter(lot_id, condition=None):
    q = DBSession.query(LotEntryWish
    ).filter(
        LotEntry.lot_id==lot_id
    ).filter(
        LotEntryWish.lot_entry_id==LotEntry.id
    ).filter(
        ShippingAddress.id==LotEntry.shipping_address_id
    ).order_by(
        LotEntryWish.wish_order
    )

    if condition is not None:
        q = q.filter(condition)

    for entry in q:
        yield _entry_info(entry)

def format_sex(s):
    if s is None:
        return u""
    v = int(s)
    if v == int(SexEnum.Male):
        return u"男性"
    elif v == int(SexEnum.Female):
        return u"女性"
    else:
        return u"未回答"

def _entry_info(wish):
    # TODO: shipping_addressも全部追加する
    shipping_address = wish.lot_entry.shipping_address

    return {
        u"申し込み番号": wish.lot_entry.entry_no,
        u"希望順序": wish.wish_order + 1,
        u"申し込み日": wish.created_at,
        u"ユーザー種別": wish.lot_entry.membergroup,
        u"席種": u",".join([",".join([i.stock_type.name for i in p.product.items]) for p in wish.products]), # 席種 この時点で席種までちゃんと決まる
        u"枚数": wish.total_quantity, # 枚数(商品関係なし)
        # u'イベント': event.title,
        # u'会場': venue.name,
        # u'公演': performance.name,
        # u'公演コード': performance.code,
        # u'公演日': performance.start_on,

        u"商品": u",".join([p.product.name for p in wish.products]), # 商品うちわけ(参考情報)
        # u'決済方法': payment_method.name,
        # u'引取方法': delivery_method.name,

        ## shipping_address
        u'配送先姓': shipping_address.last_name,
        u'配送先名': shipping_address.first_name,
        u'配送先姓(カナ)': shipping_address.last_name_kana,
        u'配送先名(カナ)': shipping_address.first_name_kana,
        u'郵便番号': shipping_address.zip,
        u'国': shipping_address.country,
        u'都道府県': shipping_address.prefecture,
        u'市区町村': shipping_address.city,
        u'住所1': shipping_address.address_1,
        u'住所2': shipping_address.address_2,
        u'電話番号1': shipping_address.tel_1,
        u'電話番号2': shipping_address.tel_2,
        u'FAX': shipping_address.fax,
        u'メールアドレス1': shipping_address.email_1,
        u'メールアドレス2': shipping_address.email_2,

        ## user_profile
        # u'姓': user_profile.last_name,
        # u'名': user_profile.first_name,
        # u'姓(カナ)': user_profile.last_name_kana,
        # u'名(カナ)': user_profile.first_name_kana,
        # u'ニックネーム': user_profile.nick_name,
        # u'性別': user_profile.sex,
    }



def submit_lot_entries(lot_id, entries):
    """
    当選リストの取り込み
    entries : (entry_no, wish_order)のリスト
    """

    for entry_no, wish_order in entries:
        w = LotElectWork(lot_id=lot_id, lot_entry_no=entry_no, wish_order=wish_order,
            entry_wish_no="{0}-{1}".format(entry_no, wish_order))
        DBSession.add(w)
    DBSession.flush()



def elect_lot_entries(request, lot_id):
    # 当選処理
    lot = DBSession.query(Lot).filter_by(id=lot_id).one()
    #electing = request.registry.adapters.lookup([Lot, IRequest], IElecting, "")
    #elector = electing(lot, request)

    elector = request.registry.queryMultiAdapter([lot, request], IElecting, "")
    return elector.elect_lot_entries()
    

def entry_session(request, lot_entry=None):
    if lot_entry is not None:
        request.session['lots.entry_id'] = lot_entry.id
    else:
        entry_id = request.session.get('lots.entry_id')
        if entry_id is None:
            return None
        
        lot_entry = DBSession.query(LotEntry).filter(LotEntry.id==entry_id).first()
        if lot_entry is not None:
            request.session['lots.entry_id'] = lot_entry.id
    return lot_entry
    
def create_cart(request, lot_entry):
    """
    """
    elected = lot_entry.lot_elected_entries
    assert elected # TODO: 例外クラス作成
    elected = elected[0]
    wish = elected.lot_entry_wish
    performance_id = wish.performance_id
    payment_delivery_method_pair = lot_entry.payment_delivery_method_pair
    cart = Cart.create(lot_entries=[lot_entry], 
        system_fee=payment_delivery_method_pair.system_fee,
        payment_delivery_pair=payment_delivery_method_pair, 
        shipping_address=lot_entry.shipping_address,
        performance=wish.performance,
        sales_segment=lot_entry.lot.sales_segment)
    wished_products = [(p.product, p.quantity) for p in wish.products]

    # 在庫処理
    stocker = cart_api.get_stocker(request)
    taked_stocks = stocker.take_stock(performance_id, wished_products)

    # TODO: 取得した在庫内容チェック
    
    # 当選した希望の商品追加
    cart.add_products(wished_products)
    return cart

def get_ordered_lot_entry(order):
    """
    order - cart - lot_entry
    """
    return DBSession.query(LotEntry).filter(
        LotEntry.cart_id==Cart.id
    ).filter(
        Cart.order_id==order.id
    ).first()

def notify_entry_lot(request, entry):
    event = LotEntriedEvent(request, entry)
    request.registry.notify(event)

def send_result_mails(request):
    """ 当選落選メール送信
    """
    send_elected_mails(request)
    send_rejected_mails(request)

def send_elected_mails(request):
    q = DBSession.query(LotElectedEntry).filter(LotElectedEntry.mail_sent_at==None).all()

    for elected_entry in q:
        sendmail.send_elected_mail(request, elected_entry)
        elected_entry.mail_sent_at = datetime.now()
        transaction.commit()

def send_rejected_mails(request):
    q = DBSession.query(LotRejectedEntry).filter(LotRejectedEntry.mail_sent_at==None).all()

    for rejected_entry in q:
        sendmail.send_rejected_mail(request, rejected_entry)
        rejected_entry.mail_sent_at = datetime.now()
        transaction.commit()

def get_entry_user(request):
    return None

def new_lot_entry(request, wishes, payment_delivery_method_pair_id, shipping_address_dict, gender, birthday, memo):
    request.session['lots.entry'] = dict(
        token=uuid4().hex,
        wishes=list(wishes),
        payment_delivery_method_pair_id=payment_delivery_method_pair_id,
        shipping_address=shipping_address_dict,
        gender=gender,
        birthday=birthday,
        memo=memo
        )
    return cart_api.new_order_session(
        request,
        client_name=shipping_address_dict["last_name"] + shipping_address_dict["first_name"],
        payment_delivery_method_pair_id=payment_delivery_method_pair_id,
        email_1=shipping_address_dict["email_1"],
        )

class Options(object):
    OPTIONS_KEY = 'altair.lots.options'

    def __init__(self, request, lot_id):
        self.request = request
        self.lot_id = lot_id
        options_map = request.session.get(self.OPTIONS_KEY)
        if not isinstance(options_map, dict):
            request.session[self.OPTIONS_KEY] = options_map = {}
        self.options_map = options_map
        options = options_map.get(lot_id)
        if options is None:
            self.options_map[lot_id] = options = []
        self.options = options

    def __del__(self):
        self.request.session.persist()

    def dispose(self):
        self.options = None
        del self.options_map[self.lot_id]

    def performance_selected(self, performance_id):
        for data in self.options:
            if data['performance_id'] == performance_id:
                return True
        return False

    def __setitem__(self, index, data):
        if len(self.options) == index:
            self.options.append(data)
        else:
            self.options[index] = data

    def __getitem__(self, index):
        return self.options[index]

    def __len__(self):
        return len(self.options)

    def __iter__(self):
        return iter(self.options_map[self.lot_id])

def get_options(request, lot_id):
    return Options(request, lot_id)
