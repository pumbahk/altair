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
from collections import OrderedDict
from markupsafe import Markup
from uuid import uuid4
from sqlalchemy import sql
from sqlalchemy.orm.exc import NoResultFound
#from pyramid.interfaces import IRequest
from webob.multidict import MultiDict
from altair.now import get_now
from ..products import api as product_api
from altair.app.ticketing.cart import api as cart_api
from altair.app.ticketing.utils import sensible_alnum_encode
from altair.app.ticketing.core import api as core_api
from altair.app.ticketing.core.models import SalesSegmentKindEnum

from altair.app.ticketing.core.models import (
    Event,
    SalesSegment,
    SalesSegmentGroup,
    ShippingAddress,
    DBSession,
    Performance,
    Product,
)
from altair.app.ticketing.i18n import custom_locale_negotiator
from altair.app.ticketing.users.models import (
    MemberGroup_SalesSegment,
    MemberGroup,
    Membership,
    SexEnum,
    UserPointAccount,
)
from altair.app.ticketing.cart.models import (
    Cart,
)
from altair.app.ticketing.cart.exceptions import NoCartError
from altair.app.ticketing.cart.view_support import coerce_extra_form_data
from .models import (
    Lot,
    LotEntry,
    LotEntryWish,
    LotEntryProduct,
    LotElectedEntry,
    LotRejectedEntry,
    #LotElectWork,
    TemporaryLotEntryWish,
    TemporaryLotEntryProduct,
)
from altair.app.ticketing.payments.api import set_confirm_url
from altair.app.ticketing.payments.payment import Payment
from altair.app.ticketing.payments.plugins import MULTICHECKOUT_PAYMENT_PLUGIN_ID, PGW_CREDIT_CARD_PAYMENT_PLUGIN_ID
from altair.multicheckout.api import get_multicheckout_3d_api
from altair.app.ticketing.events.sales_segments.resources import SalesSegmentAccessor

from . import sendmail
from .events import LotEntriedEvent
from .interfaces import IElecting
from .adapters import LotSessionCart
from . import schemas
from . import urls

LOT_ENTRY_DICT_KEY = 'lots.entry'
LOT_ENTRY_POINT_USER = 'lots.entry.point_user'

def get_event(request):
    event_id = request.matchdict['event_id']
    return Event.query.filter(Event.id==event_id).one()

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

def get_lot_entry_dict(request):
    return request.session.get(LOT_ENTRY_DICT_KEY)

def get_entry_cart(request):
    entry = get_lot_entry_dict(request)
    if entry is None:
        raise NoCartError('Cart is not associated to the request (lots)')
    try:
        lot = Lot.query.filter(Lot.id==entry['lot_id']).one()
    except NoResultFound:
        raise NoCartError("Cart is associated with a non-existent lot!")
    cart = LotSessionCart(entry, request, lot)
    return cart

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

def build_lot_entry(lot, wishes, payment_delivery_method_pair, membergroup=None, shipping_address=None, user=None, gender=None, birthday=None, memo=None, channel=None, membership=None):
    entry = LotEntry(
        lot=lot,
        user=user,
        organization_id=lot.organization_id,
        shipping_address=shipping_address,
        membergroup=membergroup,
        payment_delivery_method_pair=payment_delivery_method_pair,
        gender=gender,
        birthday=birthday,
        memo=memo,
        channel=channel,
        membership=membership
        )
    for i, wish_rec in enumerate(wishes):
        wish = build_lot_entry_wish(i, wish_rec)
        wish.organization_id = lot.organization_id
        for p in wish.products:
            p.organization_id = lot.organization_id
        entry.wishes.append(wish)
    return entry

def build_temporary_wishes(wishes,
                           payment_delivery_method_pair,
                           sales_segment):
    """ 表示用のオンメモリモデルを作成する """
    results = []
    for i, wish_rec in enumerate(wishes):
        performance_id = long(wish_rec["performance_id"])
        performance = Performance.query.filter(Performance.id==performance_id).one()
        wish = TemporaryLotEntryWish(i, performance,
                                     payment_delivery_method_pair,
                                     sales_segment)

        for wished_product_rec in wish_rec["wished_products"]:
            if wished_product_rec['quantity'] > 0:
                product = TemporaryLotEntryProduct(
                    quantity=wished_product_rec["quantity"],
                    product=Product.query.filter(Product.id==wished_product_rec["product_id"]).first()
                )
                wish.products.append(product)
        results.append(wish)
    return results


def prepare1_for_payment(request, entry_dict):
    cart = LotSessionCart(entry_dict, request, request.context.lot)

    payment = Payment(cart, request)
    set_confirm_url(request, urls.entry_confirm(request))

    # マルチ決済のみオーソリのためにカード番号入力画面に遷移する
    return payment.call_prepare()


def prepare2_for_payment(request, entry_dict, user):
    # FIXME: マルチ決済のときだけ、 keep_authorization を実行する
    cart = LotSessionCart(entry_dict, request, request.context.lot)
    if cart.payment_delivery_pair.payment_method.payment_plugin_id == MULTICHECKOUT_PAYMENT_PLUGIN_ID:
        multicheckout_api = get_multicheckout_3d_api(
            request,
            override_name=cart.lot.event.organization.setting.multicheckout_shop_name
            )
        multicheckout_api.keep_authorization(cart.order_no, u"lots")
    elif cart.payment_delivery_pair.payment_method.payment_plugin_id == PGW_CREDIT_CARD_PAYMENT_PLUGIN_ID:
        email = entry_dict.get(u'shipping_address').get('email_1') if entry_dict.get(u'shipping_address') else None
        user_id = user.id if user else None  # 認証方式によってuserがNoneとなるのを考慮(認証なしなど)
        Payment(cart, request).call_get_auth(user_id, email)


def entry_lot(request, entry_no, lot, shipping_address, wishes, payment_delivery_method_pair, user, gender, birthday, memo, extra=[], user_point_accounts=[], orion_ticket_phone=None):
    """
    wishes
    {product_id, quantity} の希望順リスト
    :param user: ゲストの場合は None
    """

    channel = core_api.get_channel(request=request)
    info = request.altair_auth_info
    entry = build_lot_entry(
        lot=lot,
        wishes=wishes,
        membergroup=cart_api.get_member_group(request, info),
        membership=cart_api.get_membership(info),
        payment_delivery_method_pair=payment_delivery_method_pair,
        shipping_address=shipping_address,
        user=user,
        gender=gender,
        birthday=birthday,
        memo=memo,
        channel=channel.v
        )
    entry.browserid = getattr(request, 'browserid', '')
    entry.user_agent = getattr(request, 'user_agent', '')
    entry.cart_session_id = getattr(request.session, 'id', '')
    entry.user_point_accounts = user_point_accounts if user_point_accounts is not None else []

    if extra:
        entry.attributes = coerce_extra_form_data(request, extra)

    entry.entry_no = entry_no
    DBSession.add(entry)
    if orion_ticket_phone:
        DBSession.add(orion_ticket_phone)
    DBSession.flush()

    for wish in entry.wishes:
        wish.entry_wish_no = "{0}-{1}".format(entry.entry_no, wish.wish_order)
    request.session['altair.lots.entry_id'] = entry.id

    return entry


def add_lot_entry_attributes(request, extra, lot_entry):
    from altair.app.ticketing.cart.view_support import get_extra_form_schema, DummyCartContext
    schema = get_extra_form_schema(
        DummyCartContext(request, order),
        request,
        order.sales_segment
        )


def get_entry(request, entry_no, tel_no):
    return LotEntry.query.filter(
        LotEntry.entry_no==entry_no,
    ).filter(
        sql.or_(ShippingAddress.tel_1==tel_no,
            ShippingAddress.tel_2==tel_no)
    ).filter(
        ShippingAddress.id==LotEntry.shipping_address_id
    ).first()


def generate_entry_no(request, organization):
    """ 引き替え用の抽選申し込み番号生成"""
    return core_api.get_next_order_no(request, organization)


def get_lot_entries_iter(lot_id, condition=None):
    q = DBSession.query(LotEntryWish
    ).filter(
        LotEntry.lot_id==lot_id
    ).filter(
        LotEntryWish.lot_entry_id==LotEntry.id
    ).filter(
        ShippingAddress.id==LotEntry.shipping_address_id
    ).order_by(
        LotEntry.entry_no,
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
    user = wish.lot_entry.user
    event = wish.lot_entry.lot.event
    performance = wish.performance
    venue = performance.venue
    pdmp = wish.lot_entry.payment_delivery_method_pair
    payment_method = pdmp.payment_method
    delivery_method = pdmp.delivery_method
    user_profile = None
    if user:
        user_profile = user.user_profile

    return OrderedDict([
        (u"状態", wish.status),
        (u"申し込み番号", wish.lot_entry.entry_no),
        (u"希望順序", wish.wish_order + 1),
        (u"申し込み日", "{0:%Y-%m-%d %H:%M}".format(wish.created_at)),
        (u"ユーザー種別", wish.lot_entry.membergroup),
        (u"席種", u",".join([",".join([i.stock_type.name for i in p.product.items]) for p in wish.products])), # 席種 この時点で席種までちゃんと決まる
        (u"枚数", wish.total_quantity), # 枚数(商品関係なし)
        (u'イベント', event.title),
        (u'会場', venue.name),
        (u'公演', performance.name),
        (u'公演コード', performance.code),
        (u'公演日', "{0:%Y-%m-%d %H:%M}".format(performance.start_on)),

        (u"商品", u",".join([p.product.name for p in wish.products])), # 商品うちわけ(参考情報)
        (u'決済方法', payment_method.name),
        (u'引取方法', delivery_method.name),

        ## shipping_address
        (u'配送先姓', shipping_address.last_name),
        (u'配送先名', shipping_address.first_name),
        (u'配送先姓(カナ)', shipping_address.last_name_kana),
        (u'配送先名(カナ)', shipping_address.first_name_kana),
        (u'郵便番号', shipping_address.zip),
        (u'国', shipping_address.country),
        (u'都道府県', shipping_address.prefecture),
        (u'市区町村', shipping_address.city),
        (u'住所1', shipping_address.address_1),
        (u'住所2', shipping_address.address_2),
        (u'電話番号1', shipping_address.tel_1),
        (u'電話番号2', shipping_address.tel_2),
        (u'FAX', shipping_address.fax),
        (u'メールアドレス1', shipping_address.email_1),
        (u'メールアドレス2', shipping_address.email_2),

        ## user_profile
        (u'姓', user_profile.last_name if user_profile else u""),
        (u'名', user_profile.first_name if user_profile else u""),
        (u'姓(カナ)', user_profile.last_name_kana if user_profile else u""),
        (u'名(カナ)', user_profile.first_name_kana if user_profile else u""),
        (u'ニックネーム', user_profile.nick_name if user_profile else u""),
        (u'性別', user_profile.sex if user_profile else u""),
    ])



def submit_lot_entries(lot_id, entries):
    """
    当選リストの取り込み
    entries : (entry_no, wish_order)のリスト
    """
    lot = Lot.query.filter(Lot.id==lot_id).one()
    return lot.elect_wishes(entries)

def submit_reject_entries(lot_id, entries):
    """
    落選リストの取り込み
    entries : entry_noのリスト
    """
    lot = Lot.query.filter(Lot.id==lot_id).one()
    return lot.reject_entries(entries)

def submit_reset_entries(lot_id, entries):
    """
    申込リストの取り込み
    entries : entry_noのリスト
    """
    lot = Lot.query.filter(Lot.id==lot_id).one()
    return lot.reset_entries(entries)


def elect_lot_entries(request, lot_id):
    # 当選処理
    lot = DBSession.query(Lot).filter_by(id=lot_id).one()

    elector = request.registry.queryMultiAdapter([lot, request], IElecting, "")
    return elector.elect_lot_entries()

def reject_lot_entries(request, lot_id):
    # 落選
    lot = DBSession.query(Lot).filter_by(id=lot_id).one()

    elector = request.registry.queryMultiAdapter([lot, request], IElecting, "")
    return elector.reject_lot_entries()

# review用 XXX: Resourceに移動
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

# def create_cart(request, lot_entry):
#     """
#     """
#     elected = lot_entry.lot_elected_entries
#     assert elected # TODO: 例外クラス作成
#     elected = elected[0]
#     wish = elected.lot_entry_wish
#     performance_id = wish.performance_id
#     payment_delivery_method_pair = lot_entry.payment_delivery_method_pair
#     cart = Cart.create(request, lot_entries=[lot_entry],
#         system_fee=payment_delivery_method_pair.system_fee,
#         payment_delivery_pair=payment_delivery_method_pair,
#         shipping_address=lot_entry.shipping_address,
#         performance=wish.performance,
#         sales_segment=lot_entry.lot.sales_segment)
#     wished_products = [(p.product, p.quantity) for p in wish.products]

#     # 在庫処理
#     stocker = cart_api.get_stocker(request)
#     taked_stocks = stocker.take_stock(performance_id, wished_products)

#     # TODO: 取得した在庫内容チェック

#     # 当選した希望の商品追加
#     cart.add_products(wished_products)
#     return cart

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


def send_election_mails(request, lot_id):
    lot = DBSession.query(Lot).filter_by(id=lot_id).one()
    elector = request.registry.queryMultiAdapter([lot, request], IElecting, "")
    return elector.send_election_mails()


def send_rejection_mails(request, lot_id):
    lot = DBSession.query(Lot).filter_by(id=lot_id).one()
    elector = request.registry.queryMultiAdapter([lot, request], IElecting, "")
    return elector.send_rejection_mails()


def get_entry_user(request):
    return cart_api.get_auth_info(request)


def new_lot_entry(request, entry_no, wishes, payment_delivery_method_pair_id, shipping_address_dict, gender, birthday, memo, extra, orion_ticket_phone, review_password):
    request.session[LOT_ENTRY_DICT_KEY] = dict(
        lot_id=request.context.lot.id,
        entry_no=entry_no,
        token=uuid4().hex,
        wishes=list(wishes),
        payment_delivery_method_pair_id=payment_delivery_method_pair_id,
        shipping_address=shipping_address_dict,
        gender=gender,
        birthday=birthday,
        memo=memo,
        extra=extra,
        orion_ticket_phone=orion_ticket_phone,
        review_password=review_password
        )
    return cart_api.new_order_session(
        request,
        client_name=get_client_name(request, shipping_address_dict),
        payment_delivery_method_pair_id=payment_delivery_method_pair_id,
        email_1=shipping_address_dict["email_1"],
        )

def get_client_name(request, shipping_address_dict):
    client_name = shipping_address_dict["last_name"] + shipping_address_dict["first_name"]
    if request.organization.setting.i18n and custom_locale_negotiator(request) != u'ja':
        client_name = convert_hankaku_to_zenkaku(client_name)
    return client_name

ASCII_HAN_ZEN_MAP = {
    u'a': u'ａ', u'b': u'ｂ', u'c': u'ｃ', u'd': u'ｄ', u'e': u'ｅ', u'f': u'ｆ', u'g': u'ｇ', u'h': u'ｈ', u'i': u'ｉ',
    u'j': u'ｊ', u'k': u'ｋ', u'l': u'ｌ', u'm': u'ｍ', u'n': u'ｎ', u'o': u'ｏ', u'p': u'ｐ', u'q': u'ｑ', u'r': u'ｒ',
    u's': u'ｓ', u't': u'ｔ', u'u': u'ｕ', u'v': u'ｖ', u'w': u'ｗ', u'x': u'ｘ', u'y': u'ｙ', u'z': u'ｚ', u'A': u'Ａ',
    u'B': u'Ｂ', u'C': u'Ｃ', u'D': u'Ｄ', u'E': u'Ｅ', u'F': u'Ｆ', u'G': u'Ｇ', u'H': u'Ｈ', u'I': u'Ｉ', u'J': u'Ｊ',
    u'K': u'Ｋ', u'L': u'Ｌ', u'M': u'Ｍ', u'N': u'Ｎ', u'O': u'Ｏ', u'P': u'Ｐ', u'Q': u'Ｑ', u'R': u'Ｒ', u'S': u'Ｓ',
    u'T': u'Ｔ', u'U': u'Ｕ', u'V': u'Ｖ', u'W': u'Ｗ', u'X': u'Ｘ', u'Y': u'Ｙ', u'Z': u'Ｚ', u'!': u'！', u'"': u'”',
    u'#': u'＃', u'$': u'＄', u'%': u'％', u'&': u'＆', u'\'': u'’', u'(': u'（', u')': u'）', u'*': u'＊', u'+': u'＋',
    u',': u'，', u'-': u'−', u'.': u'．', u'/': u'／', u':': u'：', u';': u'；', u'<': u'＜', u'=': u'＝', u'>': u'＞',
    u'?': u'？', u'@': u'＠', u'[': u'［', u'\\': u'¥', u']': u'］', u'^': u'＾', u'_': u'＿', u'`': u'‘', u'{': u'｛',
    u'|': u'｜', u'}': u'｝', u'~': u'〜', u' ': u'　'
}

def convert_hankaku_to_zenkaku(s):
    han_s = u''
    for c in s:
        try:
            han_s += ASCII_HAN_ZEN_MAP[c]
        except KeyError:
            pass
    return han_s

def clear_lot_entry(request):
    try:
        if request.session:
            del request.session[LOT_ENTRY_DICT_KEY]
    except KeyError:
        pass

def get_user_point_account_from_session(request):
    from altair.app.ticketing.users.models import User
    user_point_account_id = request.session.get(LOT_ENTRY_POINT_USER)
    return UserPointAccount.query.filter_by(id=user_point_account_id).first()

def set_user_point_account_to_session(request, user_point_account):
    request.session[LOT_ENTRY_POINT_USER] = user_point_account.id if user_point_account is not None else None

def clear_user_point_account_from_session(request):
    try:
        if request.session:
            del request.session[LOT_ENTRY_POINT_USER]
    except KeyError:
        pass

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

    def __delitem__(self, index):
        del self.options[index]

    def __len__(self):
        return len(self.options)

    def __iter__(self):
        return iter(self.options_map[self.lot_id])

def get_options(request, lot_id):
    return Options(request, lot_id)

def get_lotting_announce_timezone(timezone):
    label = u""
    labels = dict(morning=u'午前', day=u'昼以降', evening=u'夕方以降', night=u'夜', next_morning=u'明朝')
    if timezone in labels:
        label = labels[timezone]
    return label


def _create_lot_from_form(event, form, sales_segment_group=None, lot_name=None):
    if not lot_name:
        lot_name = form.data['name']
    lot = Lot(
        event=event,
        organization_id=event.organization_id,
        name=lot_name,
        limit_wishes=form.data['limit_wishes'],
        entry_limit=form.data['entry_limit'],
        description=form.data['description'],
        lotting_announce_datetime=form.data['lotting_announce_datetime'],
        lotting_announce_timezone=form.data['lotting_announce_timezone'],
        custom_timezone_label=form.data['custom_timezone_label'],
        auth_type=form.data['auth_type'],
        lot_entry_user_withdraw=form.data['lot_entry_user_withdraw']
        )
    return lot


def _create_lot_from_object(event, lot):
    lot = Lot(
        event=event,
        organization_id=event.organization_id,
        name=lot.name,
        limit_wishes=lot.limit_wishes,
        entry_limit=lot.entry_limit,
        description=lot.description,
        lotting_announce_datetime=lot.lotting_announce_datetime,
        lotting_announce_timezone=lot.lotting_announce_timezone,
        custom_timezone_label=lot.custom_timezone_label,
        auth_type=lot.auth_type,
        lot_entry_user_withdraw=lot.lot_entry_user_withdraw
        )
    return lot


def _create_lot_sales_segment(sales_segment_group, lot, sales_segment_group_id):
    accessor = SalesSegmentAccessor()
    sales_segment = accessor.create_sales_segment_for_lot(sales_segment_group, lot)
    sales_segment.sales_segment_group_id = sales_segment_group_id
    sales_segment.start_at = sales_segment_group.start_at
    sales_segment.end_at = sales_segment_group.end_at
    sales_segment.max_quantity = sales_segment_group.max_quantity
    sales_segment.seat_choice = False
    sales_segment.auth3d_notice = sales_segment_group.auth3d_notice
    sales_segment.account_id = sales_segment_group.account_id
    return sales_segment


def _copy_lot_sales_segment_between_sales_segment_group(sales_segment_group, new_sales_segment_group, lot):
    accessor = SalesSegmentAccessor()
    sales_segment = accessor.create_sales_segment_for_lot(new_sales_segment_group, lot)
    sales_segment.sales_segment_group_id = new_sales_segment_group.id
    sales_segment.start_at = sales_segment_group.start_at
    sales_segment.end_at = sales_segment_group.end_at
    sales_segment.max_quantity = sales_segment_group.max_quantity
    sales_segment.seat_choice = False
    sales_segment.auth3d_notice = sales_segment_group.auth3d_notice
    sales_segment.account_id = sales_segment_group.account_id
    return sales_segment


def create_lot(event, form, sales_segment_group=None, lot_name=None):
    if sales_segment_group:
        sales_segment_group_id = sales_segment_group.id
    else:
        sales_segment_group_id = form.data['sales_segment_group_id']
        sales_segment_group = SalesSegmentGroup.query.filter(SalesSegmentGroup.id == form.data['sales_segment_group_id']).one()
    new_lot = _create_lot_from_form(event, form, sales_segment_group, lot_name)
    _create_lot_sales_segment(sales_segment_group, new_lot, sales_segment_group_id)
    return new_lot


def create_lot_products(sales_segment_group, lot, exclude_performances=[]):
    exclude_sales_segments_ids = []
    if exclude_performances:
        exclude_sales_segments = SalesSegment.query.filter(SalesSegment.performance_id.in_(exclude_performances)).all()
        exclude_sales_segments_ids = [s.id for s in exclude_sales_segments]

    for sales_segment in sales_segment_group.sales_segments:
        for product in sales_segment.products:
            if sales_segment.id in exclude_sales_segments_ids:
                # 除外指定されたものは、コピーしない
                continue

            if not sales_segment.performance_id:
                continue

            if not product.original_product_id:
                product_api.add_lot_product(
                    lot=lot,
                    original_product=product
                )


def copy_lot(event, form, sales_segment_group, lot_name, exclude_performances):
    lot = create_lot(event, form, sales_segment_group, lot_name)
    DBSession.add(lot)
    create_lot_products(sales_segment_group, lot, exclude_performances)


def copy_lots_between_sales_segmnent(sales_segment, new_sales_segment):
    lot = Lot.query.filter(Lot.sales_segment_id == sales_segment.id).first()
    sales_segment_group = sales_segment.sales_segment_group
    new_sales_segment_group = sales_segment.sales_segment_group
    _copy_lot_sales_segment_between_sales_segment_group(sales_segment_group, new_sales_segment_group, new_lot)
    create_lot_products(new_sales_segment_group, new_lot)


def copy_lots_between_sales_segmnent_group(sales_segment_group, new_sales_segment_group):
    for sales_segment in sales_segment_group.sales_segments:
        lots = Lot.query.filter(Lot.sales_segment_id == sales_segment.id).all()
        for lot in lots:
            new_lot = _create_lot_from_object(sales_segment_group.event, lot)
            DBSession.add(new_lot)
            _copy_lot_sales_segment_between_sales_segment_group(sales_segment_group, new_sales_segment_group, new_lot)
            create_lot_products(new_sales_segment_group, new_lot)


def copy_lots_between_performance(performance, new_performance):
    for new_sales_segment in new_performance.sales_segments:
        if not new_sales_segment.is_lottery():
            continue

        for product in new_sales_segment.products:
            new_sales_segment_group = new_sales_segment.sales_segment_group
            sales_segments_ids = [ss.id for ss in new_sales_segment_group.sales_segments]
            lots = Lot.query.filter(Lot.sales_segment_id.in_(sales_segments_ids)).all()

            for lot in lots:
                if not product.original_product_id:
                    product_api.add_lot_product(
                        lot=lot,
                        original_product=product
                    )


def copy_lot_products_from_performance(performance, lot):
    target_ss = [ss for ss in performance.sales_segments if ss.sales_segment_group == lot.sales_segment.sales_segment_group]
    for sales_segment in target_ss:
        for product in sales_segment.products:
            product_api.add_lot_product(
                lot=lot,
                original_product=product
            )


def get_description_only(extra_form_fields):
    """追加フィールドから説明文のみを抽出"""
    extra_description = []
    if not extra_form_fields:  # 追加フィールドが未設定だとNoneになる
        return extra_description

    for field_desc in extra_form_fields:
        if field_desc['kind'] == u'description_only':
            extra_description.append({
                'description': Markup(field_desc['description']),
            })

    return extra_description


def check_review_auth_password(request):
    # 取引先とイベントの受付確認用パスワード機能,有効確認
    if request.organization.setting.enable_review_password and \
            request.context.event.setting.event_enable_review_password:
        return check_auth_type(request)
    else:
        return False


def check_auth_type(request):
    auth_type_valid = False
    if request.context.cart_setting is not None:
        # カートと抽選の認証方法は楽天認証とOauth認可APIを使った認証以外fc-auth認証,Keyword認証、認証無いのみ受付確認用パスワード機能を有効
        # カート設定のタイプは標準、抽選フォームのみ有効
        if request.context.cart_setting.auth_type not in ['rakuten', 'altair.oauth_auth.plugin.OAuthAuthPlugin'] and \
                request.context.cart_setting.type in ['standard', 'lot']:
            auth_type_valid = True

        if auth_type_valid and hasattr(request.context, 'lot'):
            if request.context.lot.auth_type in ['rakuten', 'altair.oauth_auth.plugin.OAuthAuthPlugin']:
                auth_type_valid = False

    return auth_type_valid