# -*- coding: utf-8 -*-
import types
import time
import random
import hashlib
from datetime import time as _time
from enum import Enum
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.types import TypeDecorator
from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.ext import declarative
from altair.models.nervous import NervousList
from altair.models import Identifier, WithTimestamp
from .exc import FamiPortNumberingError

Base = declarative.declarative_base()

# 内部トランザクション用
_session = orm.scoped_session(orm.sessionmaker())


class FamiPortSalesChannel(Enum):
    FamiPortOnly    = 1
    WebOnly         = 2
    FamiPortAndWeb  = 3


class HardcodedModel(object):
    class __metaclass__(type):
        def __new__(mcs, name, bases, d):
            retval = type.__new__(mcs, name, bases, d)
            map_ = {}
            for k, v in d.items():
                if not k.startswith('__') and not isinstance(v, (classmethod, types.UnboundMethodType, types.FunctionType)):
                    try:
                        i = iter(v)
                    except TypeError:
                        i = (v, )
                    o = retval(*i)
                    id_ = getattr(o, 'id', None)
                    if id_ is not None:
                        map_[id_] = o
                    setattr(retval, k, o)
            setattr(retval, '__map__', map_)
            return retval

    @classmethod
    def get(cls, id):
        return cls.__map__.get(id)


class FamiPortArea(HardcodedModel):
    Nationwide     = (1, u'全国')
    Hokkaido       = (2, u'北海道')
    Tohoku         = (3, u'東北')
    Kanto          = (4, u'関東')
    Tokai          = (5, u'東海')
    Hokushinetsu   = (6, u'北信越')
    Kansai         = (7, u'関西')
    ChugokuShikoku = (8, u'中国・四国')
    KyushuOkinawa  = (9, u'九州・沖縄')

    def __init__(self, id, name):
        self.id = id
        self.name = name


class FamiPortPrefecture(HardcodedModel):
    Nationwide = (0, u'全国', FamiPortArea.Nationwide)
    Hokkaido   = (1, u'北海道', FamiPortArea.Hokkaido)
    Aomori     = (2, u'青森県', FamiPortArea.Tohoku)
    Iwate      = (3, u'岩手県', FamiPortArea.Tohoku)
    Miyagi     = (4, u'宮城県', FamiPortArea.Tohoku)
    Akita      = (5, u'秋田県', FamiPortArea.Tohoku)
    Yamagata   = (6, u'山形県', FamiPortArea.Tohoku)
    Fukushima  = (7, u'福島県', FamiPortArea.Tohoku)
    Ibaraki    = (8, u'茨城県', FamiPortArea.Kanto)
    Tochigi    = (9, u'栃木県', FamiPortArea.Kanto)
    Gunma      = (10, u'群馬県', FamiPortArea.Kanto)
    Saitama    = (11, u'埼玉県', FamiPortArea.Kanto)
    Chiba      = (12, u'千葉県', FamiPortArea.Kanto)
    Tokyo      = (13, u'東京都', FamiPortArea.Kanto)
    Kanagawa   = (14, u'神奈川県', FamiPortArea.Kanto)
    Yamanashi  = (19, u'山梨県', FamiPortArea.Kanto)
    Gifu       = (21, u'岐阜県', FamiPortArea.Tokai)
    Shizuoka   = (22, u'静岡県', FamiPortArea.Tokai)
    Aichi      = (23, u'愛知県', FamiPortArea.Tokai)
    Mie        = (24, u'三重県', FamiPortArea.Tokai)
    Niigata    = (15, u'新潟県', FamiPortArea.Hokushinetsu)
    Toyama     = (16, u'富山県', FamiPortArea.Hokushinetsu)
    Ishikawa   = (17, u'石川県', FamiPortArea.Hokushinetsu)
    Fukui      = (18, u'福井県', FamiPortArea.Hokushinetsu)
    Nagano     = (20, u'長野県', FamiPortArea.Hokushinetsu)
    Shiga      = (25, u'滋賀県', FamiPortArea.Kansai)
    Kyoto      = (26, u'京都府', FamiPortArea.Kansai)
    Osaka      = (27, u'大阪府', FamiPortArea.Kansai)
    Hyogo      = (28, u'兵庫県', FamiPortArea.Kansai)
    Nara       = (29, u'奈良県', FamiPortArea.Kansai)
    Wakayama   = (30, u'和歌山県', FamiPortArea.Kansai)
    Tottori    = (31, u'鳥取県', FamiPortArea.ChugokuShikoku)
    Shimane    = (32, u'島根県', FamiPortArea.ChugokuShikoku)
    Okayama    = (33, u'岡山県', FamiPortArea.ChugokuShikoku)
    Hiroshima  = (34, u'広島県', FamiPortArea.ChugokuShikoku)
    Yamaguchi  = (35, u'山口県', FamiPortArea.ChugokuShikoku)
    Tokushima  = (36, u'徳島県', FamiPortArea.ChugokuShikoku)
    Kagawa     = (37, u'香川県', FamiPortArea.ChugokuShikoku)
    Ehime      = (38, u'愛媛県', FamiPortArea.ChugokuShikoku)
    Kochi      = (39, u'高知県', FamiPortArea.ChugokuShikoku)
    Fukuoka    = (40, u'福岡県', FamiPortArea.KyushuOkinawa)
    Saga       = (41, u'佐賀県', FamiPortArea.KyushuOkinawa)
    Nagasaki   = (42, u'長崎県', FamiPortArea.KyushuOkinawa)
    Kumamoto   = (43, u'熊本県', FamiPortArea.KyushuOkinawa)
    Oita       = (44, u'大分県', FamiPortArea.KyushuOkinawa)
    Miyazaki   = (45, u'宮崎県', FamiPortArea.KyushuOkinawa)
    Kagoshima  = (46, u'鹿児島県', FamiPortArea.KyushuOkinawa)
    Okinawa    = (47, u'沖縄県', FamiPortArea.KyushuOkinawa)

    def __init__(self, id, name, area):
        self.id = id
        self.name = name
        self.area = area


class FamiPortPlayguide(Base, WithTimestamp):
    __tablename__ = 'FamiPortPlayguide'

    id                  = sa.Column(Identifier, nullable=False, primary_key=True, autoincrement=True)
    discrimination_code = sa.Column(sa.Integer, nullable=False)

    @property
    def name(self):
        return 'xxxxx'


class FamiPortClient(Base, WithTimestamp):
    __tablename__ = 'FamiPortClient'

    famiport_playguide_id = sa.Column(Identifier, sa.ForeignKey('FamiPortPlayguide.id'), nullable=False)
    code                  = sa.Column(sa.Unicode(24), nullable=False, primary_key=True)
    name                  = sa.Column(sa.Unicode(50), nullable=False)
    prefix                = sa.Column(sa.Unicode(3), nullable=False)  # Three-letter prefix prepended to the number generated by FamiPortOrderIdentifierSequence

    playguide             = orm.relationship(FamiPortPlayguide)


class FamiPortGenre1(Base, WithTimestamp):
    __tablename__ = 'FamiPortGenre1'
    code = sa.Column(sa.Unicode(23), primary_key=True)
    name = sa.Column(sa.Unicode(255), nullable=False)


class FamiPortGenre2(Base, WithTimestamp):
    __tablename__ = 'FamiPortGenre2'
    code = sa.Column(sa.Unicode(35), primary_key=True)
    name = sa.Column(sa.Unicode(255), nullable=False)


class FamiPortVenue(Base, WithTimestamp):
    __tablename__ = 'FamiPortVenue'

    id            = sa.Column(Identifier, primary_key=True, autoincrement=True)
    name          = sa.Column(sa.Unicode(50), nullable=False)
    name_kana     = sa.Column(sa.Unicode(200), nullable=False)
    prefecture    = sa.Column(sa.Integer, nullable=False, default=0)


class SpaceDelimitedList(TypeDecorator):
    impl = sa.Unicode

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        else:
            return u' '.join(unicode(v).strip() for v in value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        else:
            return value.split(u' ')


class MutableSpaceDelimitedList(Mutable, NervousList):
    @classmethod
    def coerce(cls, key, value):
        if not isinstance(value, MutableSpaceDelimitedList):
            try:
                i = iter(value)
            except TypeError:
                return Mutable.coerce(key, value)
            return MutableSpaceDelimitedList(i)
        else:
            return value

    def _changed(self, modified):
        self.changed()


class FamiPortEvent(Base, WithTimestamp):
    __tablename__ = 'FamiPortEvent'

    id                      = sa.Column(Identifier, primary_key=True, autoincrement=True)
    userside_id             = sa.Column(Identifier, nullable=True, index=True)
    code_1                  = sa.Column(sa.Unicode(6), nullable=False)
    code_2                  = sa.Column(sa.Unicode(4), nullable=False)
    name_1                  = sa.Column(sa.Unicode(80), nullable=False, default=u'')
    name_2                  = sa.Column(sa.Unicode(80), nullable=False, default=u'')
    sales_channel           = sa.Column(sa.Integer, nullable=False, default=FamiPortSalesChannel.FamiPortOnly.value)
    client_code             = sa.Column(sa.Unicode(24), sa.ForeignKey('FamiPortClient.code'), nullable=False)
    venue_id                = sa.Column(Identifier, sa.ForeignKey('FamiPortVenue.id'), nullable=False)
    purchasable_prefectures = sa.Column(MutableSpaceDelimitedList.as_mutable(SpaceDelimitedList(137)))
    start_at                = sa.Column(sa.DateTime(), nullable=True)
    end_at                  = sa.Column(sa.DateTime(), nullable=True)
    genre_1_code            = sa.Column(sa.Unicode(23), sa.ForeignKey('FamiPortGenre1.code'))
    genre_2_code            = sa.Column(sa.Unicode(35), sa.ForeignKey('FamiPortGenre2.code'))
    keywords                = sa.Column(MutableSpaceDelimitedList.as_mutable(SpaceDelimitedList(30000)))
    search_code             = sa.Column(sa.Unicode(20))

    client                  = orm.relationship(FamiPortClient)
    venue                   = orm.relationship(FamiPortVenue)
    genre_1                 = orm.relationship(FamiPortGenre1)
    genre_2                 = orm.relationship(FamiPortGenre2)


class FamiPortPerformanceType(Enum):
    Normal  = 1
    Spanned = 2


class FamiPortPerformance(Base, WithTimestamp):
    __tablename__ = 'FamiPortPerformance'

    id                      = sa.Column(Identifier, primary_key=True, autoincrement=True)
    userside_id             = sa.Column(Identifier, nullable=True, index=True)
    famiport_event_id       = sa.Column(Identifier, sa.ForeignKey('FamiPortEvent.id'), nullable=False)
    code                    = sa.Column(sa.Unicode(3))
    name                    = sa.Column(sa.Unicode(60))
    type                    = sa.Column(sa.Integer, nullable=False, default=FamiPortPerformanceType.Normal.value)
    searchable              = sa.Column(sa.Boolean, nullable=False, default=True)
    sales_channel           = sa.Column(sa.Integer, nullable=False, default=FamiPortSalesChannel.FamiPortOnly.value)
    start_at                = sa.Column(sa.DateTime(), nullable=True)
    ticket_name             = sa.Column(sa.Unicode(20), nullable=True)  # only valid if type == Spanned

    famiport_event = orm.relationship('FamiPortEvent')


class FamiPortSalesSegment(Base, WithTimestamp):
    __tablename__ = 'FamiPortSalesSegment'

    id                      = sa.Column(Identifier, primary_key=True, autoincrement=True)
    userside_id             = sa.Column(Identifier, nullable=True, index=True)
    famiport_performance_id = sa.Column(Identifier, sa.ForeignKey('FamiPortPerformance.id'), nullable=False)
    code                    = sa.Column(sa.Unicode(3), nullable=False)
    name                    = sa.Column(sa.Unicode(40), nullable=False)
    sales_channel           = sa.Column(sa.Integer, nullable=False, default=FamiPortSalesChannel.FamiPortOnly.value)
    published_at            = sa.Column(sa.DateTime(), nullable=True)
    start_at                = sa.Column(sa.DateTime(), nullable=False)
    end_at                  = sa.Column(sa.DateTime(), nullable=True)
    auth_required           = sa.Column(sa.Boolean, nullable=False, default=False)
    auth_message            = sa.Column(sa.Unicode(320), nullable=False, default=u'')
    seat_selection_start_at = sa.Column(sa.DateTime(), nullable=True)

    famiport_performance = orm.relationship('FamiPortPerformance')


class FamiPortRefundType(Enum):
    Type1 = 1
    Type2 = 2


class FamiPortRefund(Base, WithTimestamp):
    __tablename__ = 'FamiPortRefund'

    id                   = sa.Column(Identifier, nullable=False, primary_key=True, autoincrement=True)
    type                 = sa.Column(sa.Integer, nullable=False, default=FamiPortRefundType.Type1.value)
    send_back_due_at     = sa.Column(sa.Date(), nullable=False)
    start_at             = sa.Column(sa.DateTime(), nullable=False)
    end_at               = sa.Column(sa.DateTime(), nullable=False)
    last_serial          = sa.Column(sa.Integer, nullable=False, default=0)


class FamiPortRefundEntry(Base, WithTimestamp):
    __tablename__ = 'FamiPortRefundEntry'

    id                   = sa.Column(Identifier, primary_key=True, autoincrement=True)
    famiport_refund_id   = sa.Column(Identifier, sa.ForeignKey('FamiPortRefund.id'), nullable=False)
    serial               = sa.Column(sa.Integer, nullable=False, default=0)
    famiport_ticket_id   = sa.Column(Identifier, sa.ForeignKey('FamiPortTicket.id'), nullable=False)
    ticket_payment       = sa.Column(sa.Numeric(precision=9, scale=0))
    ticketing_fee        = sa.Column(sa.Numeric(precision=8, scale=0))
    system_fee           = sa.Column(sa.Numeric(precision=8, scale=0))
    other_fees           = sa.Column(sa.Numeric(precision=8, scale=0))
    shop_code            = sa.Column(sa.Unicode(7), nullable=False)

    refunded_at          = sa.Column(sa.DateTime()) # 払戻が店頭で実際に行われた日痔

    report_generated_at  = sa.Column(sa.DateTime()) # ファイルの生成日時

    famiport_ticket = orm.relationship('FamiPortTicket')
    famiport_refund = orm.relationship('FamiPortRefund', backref='entries')


class FamiPortOrderType(Enum):  # ReplyClassEnumと意味的には同じ
    CashOnDelivery       = 1  # 代引き
    Payment              = 2  # 前払い（後日渡し）の前払い時
    Ticketing            = 3  # 代済発券と前払い(後日渡し)の後日渡し時
    PaymentOnly          = 4  # 前払いのみ


def create_random_sequence_number(length):
    seq = ''
    while len(seq) < length:
        seq += hashlib.md5(
            (str(time.time()) + str(random.random())).encode()).hexdigest()
    seq = seq.upper()
    return seq[:length]


class DigitCodec(object):
    def __init__(self, digits):
        self.digits = digits

    def encode(self, num):
        l = len(self.digits)
        retval = []
        n = num
        while True:
            rem = n % l
            quo = n // l
            retval.insert(0, self.digits[rem])
            if quo == 0:
                break
            n = quo
        return ''.join(retval)

    def decode(self, s):
        i = 0
        sl = len(s)
        l = len(self.digits)
        retval = 0
        while i < sl:
            c = s[i]
            d = self.digits.find(c)
            if d < 0:
                raise ValueError("Invalid digit: " + c)
            retval *= l
            retval += d
            i += 1
        return retval

digit_encoder = DigitCodec("0123456789ACFGHJKLPRSUWXY")


def screw(x, s):
    x = long(x)
    return (((x & 0x3000) >> 12) \
        | ((x & 0x20) >> 3) \
        | ((x & 0x600) >> 6) \
        | ((x & 0x4000) >> 9) \
        | ((x & 0x100) >> 2) \
        | ((x & 0x38000) >> 8) \
        | ((x & 0x40) << 4) \
        | ((x & 0xfc0000) >> 7) \
        | ((x & 0x8) << 14) \
        | ((x & 0x3000000) >> 6) \
        | ((x & 0x80) << 13) \
        | ((x & 0x1c000000) >> 5) \
        | ((x & 0x1) << 24) \
        | ((x & 0xe0000000) >> 4) \
        | ((x & 0x10) << 24) \
        | ((x & 0x700000000) >> 3) \
        | ((x & 0x2) << 31) \
        | ((x & 0x1ff800000000) >> 2) \
        | ((x & 0x4) << 41) \
        | ((x & 0x800) << 33) \
        | ((x & 0x600000000000))
        ) \
        ^ s


class FamiPortBarcodeNoSequence(Base):
    __tablename__ = 'FamiPortBarcodeNoSequence'

    id = sa.Column(Identifier, primary_key=True)

    @classmethod
    def get_next_value(cls, session=_session):
        seq = cls()
        session.add(seq)
        session.flush()
        return u'%013ld' % screw(seq.id, 0x12345678901L)


class FamiPortOrderIdentifierSequence(Base):
    __tablename__ = 'FamiPortOrderIdentifierSequence'

    id = sa.Column(Identifier, primary_key=True)
    prefix = sa.Column(sa.Unicode(3), nullable=False)

    @classmethod
    def get_next_value(cls, prefix, session=_session):
        assert len(prefix) == 3
        seq = cls(prefix=prefix)
        session.add(seq)
        session.flush()
        return prefix + u'%09d' % seq.id


class FamiPortOrderTicketNoSequence(Base):
    __tablename__ = 'FamiPortOrderTicketNoSequence'

    id = sa.Column(Identifier, primary_key=True)
    value = sa.Column(sa.String(13), nullable=False, unique=True)

    @classmethod
    def get_next_value(cls, session=_session):
        for ii in range(15):  # retry count
            try:
                return cls._get_next_value(session)
            except InvalidRequestError:
                pass
        raise FamiPortNumberingError()

    @classmethod
    def _get_next_value(cls, session):
        seq = cls(value=create_random_sequence_number(13))
        session.add(seq)
        session.flush()
        return seq.value


class FamiPortExchangeTicketNoSequence(Base):
    __tablename__ = 'FamiPortExchangeTicketNoSequence'

    id = sa.Column(Identifier, primary_key=True)
    value = sa.Column(sa.String(13), nullable=False, unique=True)

    @classmethod
    def get_next_value(cls, session=_session):
        for ii in range(15):  # retry count
            try:
                return cls._get_next_value(session)
            except InvalidRequestError:
                pass
        raise FamiPortNumberingError()

    @classmethod
    def _get_next_value(cls, session):
        seq = cls(value=create_random_sequence_number(13))
        session.add(seq)
        session.flush()
        return seq.value


class FamiPortReserveNumberSequence(Base):
    __tablename__ = 'FamiPortReserveNumberSequence'

    id = sa.Column(Identifier, primary_key=True)
    value = sa.Column(sa.String(13), nullable=False, unique=True)

    @classmethod
    def get_next_value(cls, session):
        for ii in range(15):  # retry count
            try:
                return cls._get_next_value(session)
            except InvalidRequestError:
                pass
        raise FamiPortNumberingError()

    @classmethod
    def _get_next_value(cls, session):
        seq = cls(value=create_random_sequence_number(13))
        session.add(seq)
        session.flush()
        return seq.value


class FamiPortOrder(Base, WithTimestamp):
    __tablename__ = 'FamiPortOrder'

    id                           = sa.Column(Identifier, primary_key=True, autoincrement=True)
    type                         = sa.Column(sa.Integer, nullable=False)
    order_no                     = sa.Column(sa.Unicode(12), nullable=False)
    famiport_order_identifier    = sa.Column(sa.Unicode(12), nullable=False)  # 注文ID
    shop_code                    = sa.Column(sa.Unicode(6), nullable=True)
    famiport_sales_segment_id    = sa.Column(Identifier, sa.ForeignKey('FamiPortSalesSegment.id'), nullable=False)
    client_code                  = sa.Column(sa.Unicode(24), sa.ForeignKey('FamiPortClient.code'), nullable=False)
    generation                   = sa.Column(sa.Integer, nullable=False, default=0)
    invalidated_at               = sa.Column(sa.DateTime(), nullable=True)
    total_amount                 = sa.Column(sa.Numeric(precision=16, scale=0), nullable=False)  # 入金金額
    ticket_payment               = sa.Column(sa.Numeric(precision=9, scale=0), nullable=False)
    ticketing_fee                = sa.Column(sa.Numeric(precision=8, scale=0), nullable=False)  # 店頭発券手数料
    system_fee                   = sa.Column(sa.Numeric(precision=8, scale=0), nullable=False)  # システム利用料
    paid_at                      = sa.Column(sa.DateTime(), nullable=True)
    issued_at                    = sa.Column(sa.DateTime(), nullable=True)
    canceled_at                  = sa.Column(sa.DateTime(), nullable=True)
    cancel_reason                = sa.Column(sa.Integer, nullable=True)

    ticketing_start_at = sa.Column(sa.DateTime(), nullable=True)
    ticketing_end_at = sa.Column(sa.DateTime(), nullable=True)
    payment_start_at = sa.Column(sa.DateTime(), nullable=True)
    payment_due_at = sa.Column(sa.DateTime(), nullable=True)

    reserve_number            = sa.Column(sa.Unicode(13), nullable=True)  # 予約番号
    exchange_number           = sa.Column(sa.Unicode(13), nullable=True)  # 引換票番号(後日予済アプリで発券するための予約番号)

    customer_name = sa.Column(sa.Unicode(42), nullable=False)  # 氏名
    customer_name_input = sa.Column(sa.Boolean, nullable=False, default=0)  # 氏名要求フラグ
    customer_phone_input = sa.Column(sa.Boolean, nullable=False, default=0)  # 電話番号要求フラグ
    customer_address_1 = sa.Column(sa.Unicode(200), nullable=False, default=u'')  # 住所1
    customer_address_2 = sa.Column(sa.Unicode(200), nullable=False, default=u'')  # 住所2
    customer_phone_number = sa.Column(sa.Unicode(12), nullable=False)  # 電話番号

    report_generated_at       = sa.Column(sa.DateTime(), nullable=True)

    famiport_sales_segment = orm.relationship('FamiPortSalesSegment')
    famiport_client = orm.relationship('FamiPortClient')

    @property
    def performance_start_at(self):
        return self.famiport_sales_segment and self.famiport_sales_segment.famiport_performance and self.famiport_sales_segment.famiport_performance.start_at

    @classmethod
    def get_by_reserveNumber(cls, reserveNumber, authNumber=None, session=_session):
        return session \
            .query(cls) \
            .filter(cls.reserve_number == reserveNumber) \
            .filter(cls.invalidated_at == None) \
            .one()
            # .filter(amitoPortOrder.auth_number == authNumber) \

    @classmethod
    def get_by_barCodeNo(cls, barCodeNo, session=_session):
        return session \
            .query(cls) \
            .join(FamiPortReceipt) \
            .filter(FamiPortReceipt.barcode_no == barCodeNo) \
            .filter(cls.invalidated_at.is_(None)) \
            .one()

    @property
    def ticket_total_count(self):
        return len(self.famiport_tickets)

    @property
    def ticket_count(self):
        return sum(0 if famiport_ticket.is_subticket else 1 for famiport_ticket in self.famiport_tickets)

    @property
    def subticket_count(self):
        return sum(1 if famiport_ticket.is_subticket else 0 for famiport_ticket in self.famiport_tickets)

    @property
    def customer_member_id(self):
        return ''  # TODO Set customer_member_id

    @property
    def customer_identify_no(self):
        return ''  # TODO Set customer_identify_no

    auth_number = None

    @property
    def current_receipt(self):
        for receipt in self.famiport_receipts:
            if receipt.completed_at or receipt.rescued_at:
                return receipt
            elif receipt.payment_request_received_at and receipt.viod_at:
                return receipt

    def create_receipt(self, now, session=_session):
        famiport_receipt = FamiPortReceipt(
            inquired_at=now,
            famiport_order_id=self.id,
            barcode_no=FamiPortOrderTicketNoSequence.get_next_value(session),
            )
        session.add(famiport_receipt)
        session.commit()
        return famiport_receipt


class FamiPortTicketType(Enum):
    Ticket                 = 2
    TicketWithBarcode      = 1
    ExtraTicket            = 4
    ExtraTicketWithBarcode = 3


class FamiPortTicket(Base, WithTimestamp):
    __tablename__ = 'FamiPortTicket'

    id                        = sa.Column(Identifier, primary_key=True, autoincrement=True)
    famiport_order_id         = sa.Column(Identifier, sa.ForeignKey('FamiPortOrder.id'), nullable=False)
    type                      = sa.Column(sa.Integer, nullable=False, default=FamiPortTicketType.TicketWithBarcode.value)
    barcode_number            = sa.Column(sa.Unicode(13), nullable=False)
    template_code             = sa.Column(sa.Unicode(10), nullable=False)
    data                      = sa.Column(sa.Unicode(4000), nullable=False)
    issued_at                 = sa.Column(sa.DateTime(), nullable=True)

    famiport_order = orm.relationship('FamiPortOrder', backref='famiport_tickets')

    @property
    def is_subticket(self):
        return self.type in (FamiPortTicketType.ExtraTicket.value, FamiPortTicketType.ExtraTicketWithBarcode.value)


class FamiPortInformationMessage(Base, WithTimestamp):
    __tablename__ = 'FamiPortInformationMessage'
    __table_args__ = (sa.UniqueConstraint('result_code'),)

    id = sa.Column(Identifier, primary_key=True)
    result_code = sa.Column(sa.Enum('WithInformation', 'ServiceUnavailable'), unique=True, nullable=False)
    message = sa.Column(sa.Unicode(length=1000), nullable=True)

    @classmethod
    def get_message(cls, information_result_code, default_message=None, session=_session):
        from .communication import InformationResultCodeEnum
        assert isinstance(information_result_code, InformationResultCodeEnum)
        query = session.query(FamiPortInformationMessage).filter_by(result_code=information_result_code.name)
        famiport_information_message = query.first()
        if famiport_information_message:
            return famiport_information_message.message
        else:
            return default_message


class FamiPortShop(Base, WithTimestamp):
    __tablename__ = 'FamiPortShop'

    id = sa.Column(Identifier, primary_key=True)
    code = sa.Column(sa.Unicode(5), nullable=False)
    company_code = sa.Column(sa.Unicode(4), nullable=False)
    company_name = sa.Column(sa.Unicode(40), nullable=False)
    district_code = sa.Column(sa.Unicode(1), nullable=False)
    district_name = sa.Column(sa.Unicode(40), nullable=False)
    district_valid_from = sa.Column(sa.Date(), nullable=False)
    branch_code = sa.Column(sa.Unicode(3), nullable=False)
    branch_name = sa.Column(sa.Unicode(40), nullable=False)
    branch_valid_from = sa.Column(sa.Date(), nullable=False)
    name = sa.Column(sa.Unicode(30), nullable=False)
    name_kana = sa.Column(sa.Unicode(60), nullable=False)
    tel = sa.Column(sa.Unicode(12), nullable=False)
    prefecture = sa.Column(sa.Integer(), nullable=False)
    prefecture_name = sa.Column(sa.Unicode(20), nullable=False)
    address = sa.Column(sa.Unicode(80), nullable=False)
    open_from = sa.Column(sa.Date(), nullable=True)
    zip = sa.Column(sa.Unicode(8), nullable=False)
    business_run_from = sa.Column(sa.Date(), nullable=True)
    open_at = sa.Column(sa.Time(), nullable=False, default=_time(0, 0, 0))
    close_at = sa.Column(sa.Time(), nullable=False, default=_time(0, 0, 0))
    business_hours = sa.Column(sa.Integer(), nullable=False, default=1440)
    opens_24hours = sa.Column(sa.Boolean(), nullable=False, default=True)
    closest_station = sa.Column(sa.Unicode(41), nullable=False, default=u'')
    liquor_available = sa.Column(sa.Boolean(), nullable=False, default=False)
    cigarettes_available = sa.Column(sa.Boolean(), nullable=False, default=False)
    business_run_until = sa.Column(sa.Date(), nullable=True)
    open_until = sa.Column(sa.Date(), nullable=True)
    business_paused_at = sa.Column(sa.Date(), nullable=True)
    business_continued_at = sa.Column(sa.Date(), nullable=True)
    latitude = sa.Column(sa.Numeric(precision=8, scale=6), nullable=True)
    longitude = sa.Column(sa.Numeric(precision=9, scale=6), nullable=True)
    atm_available = sa.Column(sa.Boolean(), nullable=False, default=False)
    atm_available_from = sa.Column(sa.Date(), nullable=True)
    atm_available_until = sa.Column(sa.Date(), nullable=True)
    mmk_available = sa.Column(sa.Boolean(), nullable=False, default=False)
    mmk_available_from = sa.Column(sa.Date(), nullable=True)
    mmk_available_until = sa.Column(sa.Date(), nullable=True)
    renewal_start_at = sa.Column(sa.Date(), nullable=True)
    renewal_end_at = sa.Column(sa.Date(), nullable=True)
    business_status = sa.Column(sa.Integer, nullable=False, default=0)
    paused = sa.Column(sa.Boolean(), nullable=False, default=False)
    deleted = sa.Column(sa.Boolean(), nullable=False, default=False)


class FamiPortReceipt(Base, WithTimestamp):
    __tablename__ = 'FamiPortReceipt'

    id = sa.Column(Identifier, primary_key=True)

    inquired_at = sa.Column(sa.DateTime(), nullable=True)  # 予約照会が行われた日時
    payment_request_received_at = sa.Column(sa.DateTime(), nullable=True)  # 支払/発券要求が行われた日時
    customer_request_received_at = sa.Column(sa.DateTime(), nullable=True)  # 顧客情報照会が行われた日時
    completed_at = sa.Column(sa.DateTime(), nullable=True)  # 完了処理が行われた日時
    void_at = sa.Column(sa.DateTime(), nullable=True)  # 30分voidによって無効化された日時
    rescued_at = sa.Column(sa.DateTime(), nullable=True)  # 90分救済措置にて救済された時刻

    barcode_no = sa.Column(sa.Unicode(13), nullable=False)  # 支払番号

    famiport_order_id = sa.Column(Identifier, sa.ForeignKey('FamiPortOrder.id'), nullable=False)
    famiport_order = orm.relationship('FamiPortOrder', backref='famiport_receipts')
