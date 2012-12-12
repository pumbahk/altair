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

"""

import transaction
from datetime import datetime
import itertools
from sqlalchemy import sql
from sqlalchemy.orm import joinedload
from ticketing.core.api import get_organization
import ticketing.cart.api as cart_api
from ticketing.utils import sensible_alnum_encode
from ticketing.rakuten_auth.api import authenticated_user

from ticketing.core.models import (
    Organization,
    Account,
    Event,
    SalesSegment,
    StockType,
    Stock,
    StockHolder,
    Performance,
    Product,
    ProductItem,
    ShippingAddress,
    DBSession,
)

from ticketing.users.models import (
    MemberGroup_SalesSegment,
    MemberGroup,
)
from ticketing.cart.models import (
    Cart,
)

from .models import (
    Lot,
    LotEntry,
    LotEntryWish,
    LotEntryProduct,
    Lot_Performance,
    Lot_StockType,
    LotElectedEntry,
    LotRejectedEntry,
)

from .events import LotEntriedEvent

def get_event(request):
    event_id = request.matchdict['event_id']
    return Event.query.filter(Event.id==event_id).one()

def get_products(request, sales_segment, performances):
    """ """
    # TODO: 公演ごとに在庫とひもづく商品を表示する
    # 販売区分 -> 商品 -> 商品アイテム -> 在庫 -> 公演
    products = DBSession.query(Product, Performance
    ).filter(
        Product.sales_segment_id==sales_segment.id
    ).filter(
        Product.id==ProductItem.product_id
    ).filter(
        ProductItem.performance_id.in_([p.id for p in performances])
    ).filter(
        Performance.id==ProductItem.performance_id
    ).distinct().order_by(Performance.id, Product.display_order).all()

    return products

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
            MemberGroup_SalesSegment.c.sales_segment_id==SalesSegment.id
        ).filter(
            MemberGroup_SalesSegment.c.membergroup_id==MemberGroup.id
        ).filter(
            MemberGroup.is_guest==True
        ).one()
    else:
        return SalesSegment.query.filter(
            SalesSegment.event_id==event.id
        ).filter(
            MemberGroup_SalesSegment.c.sales_segment_id==SalesSegment.id
        ).filter(
            MemberGroup_SalesSegment.c.membergroup_id==membergroup.id
        ).one()

def get_requested_lot(request):
    lot_id = request.matchdict.get('lot_id')
    return Lot.query.filter(Lot.id==lot_id).one()


def get_lot(request, event, sales_segment, lot_id):
    """ 抽選取得
    :return: 抽選, 公演リスト, 席種リスト
    """
    lot = Lot.query.filter(
        Lot.event_id==event.id
    ).filter(
        Lot.sales_segment_id==sales_segment.id
    ).filter(
        Lot.id==lot_id,
    ).one()

    performances = Performance.query.filter(
        Performance.id==Lot_Performance.c.performance_id
    ).filter(
        Lot_Performance.c.lot_id==lot.id
    ).all()

    stock_types = StockType.query.filter(
        StockType.id==Lot_StockType.c.stock_type_id
    ).filter(
        Lot_StockType.c.lot_id==lot.id
    ).all()

    return lot, performances, stock_types

def entry_lot(request, lot, shipping_address, wishes, payment_delivery_method_pair, user):
    """
    wishes
    {product_id, quantity} の希望順リスト
    :param user: ゲストの場合は None
    """
    membergroup = get_member_group(request)
    entry = LotEntry(lot=lot, shipping_address=shipping_address, membergroup=membergroup, payment_delivery_method_pair=payment_delivery_method_pair)
    wished_product_ids = itertools.chain(*[[p[1] for p in w] for w in wishes])

    products = Product.query.filter(
        Product.id.in_(wished_product_ids)
    ).all()

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
    """

    organization_code = lot_entry.lot.event.organization.code
    base_id = lot_entry.id
    return "LOT" + organization_code + sensible_alnum_encode(base_id).zfill(10)


def get_lot_entries_iter(lot_id):
    q = DBSession.query(LotEntryWish
    ).options(
        joinedload(LotEntry.shipping_address)
    ).filter(
        LotEntry.lot_id==lot_id
    ).filter(
        LotEntryWish.entry_id==LotEntry.id
    ).orderby(
        LotEntryWish.wish_order
    )

    for entry in q:
        yield _entry_info(entry)

def _entry_info(wish):
    shipping_address = wish.shipping_address

    return {
        "entry_no": wish.lot_entry.entry_no,
        "wish_order": wish.wish_order,
        "created_at": wish.created_at,
        "membergroup": wish.lot_entry.membergroup,
        "stock_type": None, # 席種
        "total_quantity": None, # 枚数(商品関係なし)
        "products": None, # 商品うちわけ(参考情報)
        "zip": shipping_address.zip,
        "prefecture": shipping_address.prefecture,
        "sex": shipping_address.sex,
    }

def submit_lot_entries(lot_id, entries):
    """
    当選リストの取り込み
    entries : (entry_no, wish_order)のリスト
    """

    lot = DBSession.query(Lot).filter(id==lot_id).one()
    assert lot.status == int(LotStatusEnum.Electing)

    for entry_no, wish_order in entries:
        w = LotElectWork(lot_id=lot_id, lot_entry_no=entry_no, wish_order=wish_order,
            entry_wish_no="{0}-{1}".format(entry_no, wish_order))
        DBSession.add(w)
    DBSession.flush()



def elect_lot_entries(lot_id):
    """ 抽選申し込み確定 
    申し込み番号と希望順で、当選確定処理を行う
    ワークに入っているものから当選処理をする
    それ以外を落選処理にする
    """


    # 当選処理
    lot = DBSession.query(Lot).filter_by(id=lot_id).one()

    elected_wishes = DBSession.query(LotEntryWish).filter(
        LotEntryWish.lot_id==lot_id
    ).filter(
        LotEntryWish.id.in_([e.id for e in entries])
    )

    for ew in elected_wishes:
        elect_entry(lot, ew)
        # TODO: 再選処理



    # 落選処理
    q = DBSession.query(LotEntry).filter(
        LotEntry.elected_at==None
    ).filter(
        LotEntry.rejected_at==None
    ).all()

    for entry in q:
        reject_entry(lot, entry)

    lot.status = int(LotStatusEnum.Elected)

def reject_entry(lot, entry):
    now = datetime.now()
    entry.rejected_at = now
    rejected = LotRejectedEntry(lot_entry=elected_wish.lot_entry)
    DBSession.add(rejected)
    return rejected

def elect_entry(lot, elected_wish):
    """ 個々の希望申し込みに対する処理 
    :return: 当選情報
    """
    now = datetime.now()
    elected_wish.elected_at = now
    elected_wish.lot_entry.elected_at = now
    elected = LotElectedEntry(lot_entry=elected_wish.lot_entry,
        lot_entry_wish=elected_wish)
    DBSession.add(elected)
    return elected

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
    cart = Cart(lot_entries=[lot_entry], 
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
    event = LotEntriedEvent(entry)
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
