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
from datetime import datetime, date
from collections import OrderedDict
from uuid import uuid4
from sqlalchemy import sql
from sqlalchemy.orm.exc import NoResultFound
#from pyramid.interfaces import IRequest
from webob.multidict import MultiDict
from altair.now import get_now
from altair.app.ticketing.cart import api as cart_api
from altair.app.ticketing.utils import sensible_alnum_encode
from altair.app.ticketing.core import api as core_api

from altair.app.ticketing.core.models import (
    Event,
    SalesSegment,
    ShippingAddress,
    DBSession,
    Performance,
    Product,
)

from altair.app.ticketing.users.models import (
    MemberGroup_SalesSegment,
    MemberGroup,
    Membership,
    SexEnum,
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
from altair.app.ticketing.payments.plugins import MULTICHECKOUT_PAYMENT_PLUGIN_ID
from altair.multicheckout.api import get_multicheckout_3d_api

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

def prepare2_for_payment(request, entry_dict):
    # FIXME: マルチ決済のときだけ、 keep_authorization を実行する
    cart = LotSessionCart(entry_dict, request, request.context.lot)
    if cart.payment_delivery_pair.payment_method.payment_plugin_id == MULTICHECKOUT_PAYMENT_PLUGIN_ID:
        multicheckout_api = get_multicheckout_3d_api(
            request,
            override_name=cart.lot.event.organization.setting.multicheckout_shop_name
            )
        multicheckout_api.keep_authorization(cart.order_no, u"lots")

def entry_lot(request, entry_no, lot, shipping_address, wishes, payment_delivery_method_pair, user, gender, birthday, memo, extra=[]):
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

    if extra:
        entry.attributes = coerce_extra_form_data(request, extra)

    entry.entry_no = entry_no
    DBSession.add(entry)
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

def send_result_mails(request):
    """ 当選落選メール送信
    """
    send_elected_mails(request)
    send_rejected_mails(request)

def send_elected_mails(request):
    q = DBSession.query(LotElectedEntry).filter(LotElectedEntry.mail_sent_at==None).all()

    for elected_entry in q:
        sendmail.send_elected_mail(request, elected_entry)
        elected_entry.mail_sent_at = get_now(request)
        transaction.commit()

def send_rejected_mails(request):
    q = DBSession.query(LotRejectedEntry).filter(LotRejectedEntry.mail_sent_at==None).all()

    for rejected_entry in q:
        sendmail.send_rejected_mail(request, rejected_entry)
        rejected_entry.mail_sent_at = get_now(request)
        transaction.commit()

def get_entry_user(request):
    return cart_api.get_auth_info(request)

def new_lot_entry(request, entry_no, wishes, payment_delivery_method_pair_id, shipping_address_dict, gender, birthday, memo, extra):
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
        extra=extra
        )
    return cart_api.new_order_session(
        request,
        client_name=shipping_address_dict["last_name"] + shipping_address_dict["first_name"],
        payment_delivery_method_pair_id=payment_delivery_method_pair_id,
        email_1=shipping_address_dict["email_1"],
        )

def clear_lot_entry(request):
    try:
        if request.session:
            del request.session[LOT_ENTRY_DICT_KEY]
    except KeyError:
        pass

def get_point_user(request):
    from altair.app.ticketing.users.models import User
    user_id = request.session.get(LOT_ENTRY_POINT_USER)
    return User.get(user_id)

def set_point_user(request, point_user):
    clear_point_user(request)
    request.session[LOT_ENTRY_POINT_USER] = point_user.id

def clear_point_user(request):
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

def create_client_form(context, request, **kwds):
    user = cart_api.get_or_create_user(context.authenticated_user())
    user_profile = None
    if user is not None:
        user_profile = user.user_profile

    retval = schemas.ClientForm(context=context, **kwds)

    # XXX:ゆるふわなデフォルト値
    sex = SexEnum.Female.v
    birthday = date(1990, 1, 1)

    """
    if user_profile is not None:
        retval.last_name.data = user_profile.last_name
        retval.last_name_kana.data = user_profile.last_name_kana
        retval.first_name.data = user_profile.first_name
        retval.first_name_kana.data = user_profile.first_name_kana
        retval.tel_1.data = user_profile.tel_1
        retval.fax.data = getattr(user_profile, "fax", None)
        retval.zip.data = user_profile.zip
        retval.prefecture.data = user_profile.prefecture
        retval.city.data = user_profile.city
        retval.address_1.data = user_profile.address_1
        retval.address_2.data = user_profile.address_2
        retval.email_1.data = user_profile.email_1
        retval.email_2.data = user_profile.email_2
        if user_profile.sex:
            sex = user_profile.sex
        if user_profile.birthday:
            birthday = user_profile.birthday
    """
    retval.sex.process_data(unicode(sex or u''))
    retval.birthday.process_data(birthday)

    if 'formdata' in kwds:
        retval.process(**kwds)  # 入力フォームの値を反映
    return retval

def get_lotting_announce_timezone(timezone):
    label = u""
    labels = dict(morning=u'午前', day=u'昼以降', evening=u'夕方以降', night=u'夜', next_morning=u'明朝')
    if timezone in labels:
        label = labels[timezone]
    return label

def enable_auto_input_form(request, user):
    from altair.app.ticketing.users.models import User
    if not isinstance(user, User):
        return False

    if user.member is None:
        # 楽天認証
        return True

    info = request.altair_auth_info
    membership = cart_api.get_membership(info)

    if membership.enable_auto_input_form:
        return True

    return False
