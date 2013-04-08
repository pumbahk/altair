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

def entry_lot(request, lot, shipping_address, wishes, payment_delivery_method_pair, user):
    """
    wishes
    {product_id, quantity} の希望順リスト
    :param user: ゲストの場合は None
    """
    membergroup = get_member_group(request)
    entry = LotEntry(lot=lot, shipping_address=shipping_address, membergroup=membergroup, payment_delivery_method_pair=payment_delivery_method_pair)


    for i, w in enumerate(wishes):
        performance_id = w["performance_id"]
        wish = LotEntryWish(lot_entry=entry, wish_order=i, performance_id=performance_id)
        for wp in w["wished_products"]:
            LotEntryProduct(lot_wish=wish, quantity=wp["quantity"], product_id=wp["product_id"])

    DBSession.add(entry)
    DBSession.flush()
    entry.entry_no = generate_entry_no(request, entry)
    for wish in entry.wishes:
        wish.entry_wish_no = "{0}-{1}".format(entry.entry_no, wish.wish_order)
    return entry

def get_entry(request, entry_no, tel_no):
    return LotEntry.query.filter(
        LotEntry.entry_no==entry_no,
    ).filter(
        sql.or_(ShippingAddress.tel_1==tel_no, 
            ShippingAddress.tel_2==tel_no)
    ).filter(
        ShippingAddress.id==LotEntry.shipping_address_id
    ).one()


def generate_entry_no(request, lot_entry):
    """ 引き替え用の抽選申し込み番号生成
    TODO:  ticketing.core.api.get_next_order_no を使う
    """
    base_id = core_api.get_next_order_no()
    organization_code = lot_entry.lot.event.organization.code
    return organization_code + sensible_alnum_encode(base_id).zfill(10)


def get_lot_entries_iter(lot_id):
    q = DBSession.query(LotEntryWish
    ).filter(
        LotEntry.lot_id==lot_id
    ).filter(
        LotEntryWish.lot_entry_id==LotEntry.id
    ).order_by(
        LotEntryWish.wish_order
    )

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
    shipping_address = wish.lot_entry.shipping_address

    return {
        u"申し込み番号": wish.lot_entry.entry_no,
        u"希望順序": wish.wish_order + 1,
        u"申し込み日": wish.created_at,
        u"ユーザー種別": wish.lot_entry.membergroup,
        u"席種": u",".join([",".join([i.stock_type.name for i in p.product.items]) for p in wish.products]), # 席種 この時点で席種までちゃんと決まる
        u"枚数": wish.total_quantity, # 枚数(商品関係なし)
        u"商品": u",".join([p.product.name for p in wish.products]), # 商品うちわけ(参考情報)
        u"郵便番号": shipping_address.zip,
        u"都道府県": shipping_address.prefecture,
        u"性別": format_sex(shipping_address.sex),
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
    electing = request.registry.adapters.lookup([Lot, IRequest], IElecting, "")
    elector = electing(lot)

    return elector.elect_lot_entries
    

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
