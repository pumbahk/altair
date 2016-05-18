# -*- coding: utf-8 -*-
import types
import logging
import time
import random
import hashlib
import struct
from decimal import Decimal
from datetime import time as _time
from enum import Enum
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.orm.session import object_session
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.types import TypeDecorator
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.ext import declarative
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm.collections import attribute_mapped_collection
from altair.models.nervous import NervousList
from altair.models import Identifier, WithTimestamp, MutableSpaceDelimitedList, SpaceDelimitedList
from . import events
from .exc import (
    FamiPortError,
    FamiPortNumberingError,
    FamiPortUnsatisfiedPreconditionError,
    )

Base = declarative.declarative_base()

logger = logging.getLogger(__name__)


class FamiPortSalesChannel(Enum):
    FamiPortOnly    = 1
    WebOnly         = 2
    FamiPortAndWeb  = 3


class FamiPortVoidReason(Enum):
    InvalidTicketData  =  1 # 券面XML不正
    LogError           =  2 # 仮取引ログ出力失敗
    DatabaseError      =  3 # アプリエラー（DBエラー）
    MiddlewareError    =  4 # アプリエラー（ミドルウェアエラー）
    UnexpectedError    =  5 # アプリエラー（予期しないエラー）
    ThirtyMinutesVoid  = 10 # 30分VOID
    Reissuing          = 99 # 再発券


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

        def __iter__(cls):
            return iter(getattr(cls, '__map__').values())

    @classmethod
    def get(cls, id):
        return cls.__map__.get(id)

    @classmethod
    def is_valid_id(cls, id):
        return id in cls.__map__


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

    id                    = sa.Column(Identifier, nullable=False, primary_key=True, autoincrement=True)
    name                  = sa.Column(sa.Unicode(50), nullable=False, default=u'')
    discrimination_code   = sa.Column(sa.Integer, nullable=False)
    discrimination_code_2 = sa.Column(sa.Integer, nullable=False) # 券面プレビューでのみ利用


class FamiPortClient(Base, WithTimestamp):
    __tablename__ = 'FamiPortClient'

    famiport_playguide_id = sa.Column(Identifier, sa.ForeignKey('FamiPortPlayguide.id'), nullable=False)
    code                  = sa.Column(sa.Unicode(24), nullable=False, primary_key=True)
    name                  = sa.Column(sa.Unicode(50), nullable=False)
    prefix                = sa.Column(sa.Unicode(3), nullable=False)  # Three-letter prefix prepended to the number generated by FamiPortOrderIdentifierSequence
    auth_number_required  = sa.Column(sa.Boolean(), nullable=False, default=False)

    playguide             = orm.relationship(FamiPortPlayguide)


class FamiPortGenre1(Base, WithTimestamp):
    __tablename__ = 'FamiPortGenre1'
    code = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.Unicode(255), nullable=False)


class FamiPortGenre2(Base, WithTimestamp):
    __tablename__ = 'FamiPortGenre2'
    __table_args__ = (
        sa.PrimaryKeyConstraint('genre_1_code', 'code'),
        )
    genre_1_code = sa.Column(sa.Integer, sa.ForeignKey('FamiPortGenre1.code'), nullable=False)
    code = sa.Column(sa.Integer, autoincrement=False)
    name = sa.Column(sa.Unicode(255), nullable=False)

    genre_1 = orm.relationship('FamiPortGenre1')


class FamiPortVenue(Base, WithTimestamp):
    __tablename__ = 'FamiPortVenue'

    id            = sa.Column(Identifier, primary_key=True, autoincrement=True)
    userside_id   = sa.Column(Identifier, nullable=True, index=True)
    client_code   = sa.Column(sa.Unicode(24), sa.ForeignKey('FamiPortClient.code'), nullable=False)
    name          = sa.Column(sa.Unicode(50), nullable=False)
    name_kana     = sa.Column(sa.Unicode(200), nullable=False)
    prefecture    = sa.Column(sa.Integer, nullable=False, default=0)


class FamiPortEvent(Base, WithTimestamp):
    __tablename__ = 'FamiPortEvent'
    __table_args__ = (
        sa.ForeignKeyConstraint(['genre_1_code', 'genre_2_code'], ['FamiPortGenre2.genre_1_code', 'FamiPortGenre2.code']),
        sa.UniqueConstraint('client_code', 'code_1', 'code_2', 'revision'),
        )

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
    genre_1_code            = sa.Column(sa.Integer, sa.ForeignKey('FamiPortGenre1.code'))
    genre_2_code            = sa.Column(sa.Integer)
    keywords                = sa.Column(MutableSpaceDelimitedList.as_mutable(SpaceDelimitedList(30000)))
    search_code             = sa.Column(sa.Unicode(20))
    revision                = sa.Column(sa.Integer, nullable=False, default=0)
    file_generated_at       = sa.Column(sa.DateTime(), nullable=True)
    invalidated_at          = sa.Column(sa.DateTime(), nullable=True)
    reflected_at            = sa.Column(sa.DateTime(), nullable=True)

    client                  = orm.relationship(FamiPortClient)
    venue                   = orm.relationship(FamiPortVenue)
    genre_1                 = orm.relationship(FamiPortGenre1)
    genre_2                 = orm.relationship(FamiPortGenre2)


class FamiPortPerformanceType(Enum):
    Normal  = 1
    Spanned = 2


class FamiPortPerformance(Base, WithTimestamp):
    __tablename__ = 'FamiPortPerformance'
    __table_args__ = (
        sa.UniqueConstraint('famiport_event_id', 'code', 'revision'),
        )
    id                      = sa.Column(Identifier, primary_key=True, autoincrement=True)
    userside_id             = sa.Column(Identifier, nullable=True, index=True)
    famiport_event_id       = sa.Column(Identifier, sa.ForeignKey('FamiPortEvent.id'), nullable=False)
    code                    = sa.Column(sa.Unicode(3), nullable=False)
    name                    = sa.Column(sa.Unicode(60), nullable=False, default=u'')
    type                    = sa.Column(sa.Integer, nullable=False, default=FamiPortPerformanceType.Normal.value)
    searchable              = sa.Column(sa.Boolean, nullable=False, default=True)
    sales_channel           = sa.Column(sa.Integer, nullable=False, default=FamiPortSalesChannel.FamiPortOnly.value)
    start_at                = sa.Column(sa.DateTime(), nullable=True)
    ticket_name             = sa.Column(sa.Unicode(20), nullable=True)  # only valid if type == Spanned
    revision                = sa.Column(sa.Integer, nullable=False, default=0)
    file_generated_at       = sa.Column(sa.DateTime(), nullable=True)
    reflected_at            = sa.Column(sa.DateTime(), nullable=True)
    invalidated_at          = sa.Column(sa.DateTime(), nullable=True)

    famiport_event = orm.relationship(
        'FamiPortEvent',
        primaryjoin=lambda: FamiPortPerformance.famiport_event_id == FamiPortEvent.id
        )

    # def delete(self):
    #     if self.orders:
    #         raise Exception(u'購入されている為、削除できません')
    #     else:
    #         # delete SalesSegment
    #         for sales_segment in self.sales_segments:
    #             sales_segment.delete()
    #
    #         super(FamiPortPerformance, self).delete()


class FamiPortSalesSegment(Base, WithTimestamp):
    __tablename__ = 'FamiPortSalesSegment'
    __table_args__ = (
        sa.UniqueConstraint('famiport_performance_id', 'code', 'revision'),
        )

    id                      = sa.Column(Identifier, primary_key=True, autoincrement=True)
    userside_id             = sa.Column(Identifier, nullable=True, index=True)
    famiport_performance_id = sa.Column(Identifier, sa.ForeignKey('FamiPortPerformance.id'), nullable=False)
    code                    = sa.Column(sa.Unicode(3), nullable=False)
    name                    = sa.Column(sa.Unicode(40), nullable=False, default=u'')
    sales_channel           = sa.Column(sa.Integer, nullable=False, default=FamiPortSalesChannel.FamiPortOnly.value)
    published_at            = sa.Column(sa.DateTime(), nullable=True)
    start_at                = sa.Column(sa.DateTime(), nullable=False)
    end_at                  = sa.Column(sa.DateTime(), nullable=True)
    auth_required           = sa.Column(sa.Boolean, nullable=False, default=False)
    auth_message            = sa.Column(sa.Unicode(320), nullable=False, default=u'')
    seat_selection_start_at = sa.Column(sa.DateTime(), nullable=True)
    revision                = sa.Column(sa.Integer, nullable=False, default=0)
    file_generated_at       = sa.Column(sa.DateTime(), nullable=True)
    reflected_at            = sa.Column(sa.DateTime(), nullable=True)
    invalidated_at          = sa.Column(sa.DateTime(), nullable=True)

    famiport_performance = orm.relationship(
        'FamiPortPerformance',
        primaryjoin=lambda: FamiPortSalesSegment.famiport_performance_id == FamiPortPerformance.id,
        backref='sales_segments'
        )


class FamiPortRefundType(Enum):
    Type1 = 1
    Type2 = 2


class FamiPortRefund(Base, WithTimestamp):
    __tablename__ = 'FamiPortRefund'

    id                   = sa.Column(Identifier, nullable=False, primary_key=True, autoincrement=True)
    type                 = sa.Column(sa.Integer, nullable=False, default=FamiPortRefundType.Type1.value)
    client_code          = sa.Column(sa.Unicode(24), sa.ForeignKey('FamiPortClient.code'), nullable=False)
    userside_id          = sa.Column(Identifier, nullable=True)
    send_back_due_at     = sa.Column(sa.Date(), nullable=False)
    start_at             = sa.Column(sa.DateTime(), nullable=False)
    end_at               = sa.Column(sa.DateTime(), nullable=False)
    last_serial          = sa.Column(sa.Integer, nullable=False, default=0)


class FamiPortRefundEntry(Base, WithTimestamp):
    __tablename__ = 'FamiPortRefundEntry'

    session = None

    id                   = sa.Column(Identifier, primary_key=True, autoincrement=True)
    famiport_refund_id   = sa.Column(Identifier, sa.ForeignKey('FamiPortRefund.id'), nullable=False)
    serial               = sa.Column(sa.Integer, nullable=False, default=0)
    famiport_ticket_id   = sa.Column(Identifier, sa.ForeignKey('FamiPortTicket.id'), nullable=False)
    ticket_payment       = sa.Column(sa.Numeric(precision=9, scale=0))
    ticketing_fee        = sa.Column(sa.Numeric(precision=8, scale=0))
    other_fees           = sa.Column(sa.Numeric(precision=8, scale=0))
    shop_code            = sa.Column(sa.Unicode(7), nullable=False)

    refunded_at          = sa.Column(sa.DateTime()) # 払戻が店頭で実際に行われた日時

    report_generated_at  = sa.Column(sa.DateTime()) # ファイルの生成日時

    famiport_ticket = orm.relationship('FamiPortTicket')
    famiport_refund = orm.relationship('FamiPortRefund', backref='entries')


class FamiPortOrderType(Enum):  # ReplyClassEnumと意味的には同じ
    CashOnDelivery       = 1  # 代引き
    Payment              = 2  # 前払い（後日渡し）
    Ticketing            = 3  # 代済発券
    PaymentOnly          = 4  # 前払いのみ


class FamiPortReceiptType(Enum):
    Payment              = 1  # 前払い（後日渡し）の前払い時
    Ticketing            = 2  # 代済発券と前払い(後日渡し)の後日渡し時
    CashOnDelivery       = 3  # 代引き


def create_random_sequence_number(length):
    seq = u''
    while len(seq) < length:
        seq += u''.join(digit_encoder.encode(i) for i in struct.unpack('QQ', hashlib.md5((str(time.time()) + str(random.random())).encode()).digest()))
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


def screw36(x, s):
    x = long(x)
    return (((x & 0x180000000) >> 31) \
        | ((x & 0x1c00) >> 8) \
        | ((x & 0x60000) >> 12) \
        | ((x & 0x60) << 2) \
        | ((x & 0x100) << 1) \
        | ((x & 0x1e000) >> 3) \
        | ((x & 0x4) << 12) \
        | ((x & 0x80) << 8) \
        | ((x & 0x1) << 16) \
        | ((x & 0x780000) >> 2) \
        | ((x & 0x8) << 18) \
        | ((x & 0x2) << 21) \
        | ((x & 0x800000000) >> 12) \
        | ((x & 0x600000000) >> 9) \
        | ((x & 0x40000000) >> 4) \
        | (x & 0x38000000) \
        | ((x & 0x3800000) << 7) \
        | ((x & 0x10) << 29) \
        | ((x & 0x200) << 25) \
        | ((x & 0x4000000) << 9) \
        ) \
        ^ s

def screw47(x, s):
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


# http://www.gs1.org/how-calculate-check-digit-manually
def calculate_gtin_cd(barcode):
    return u'%d' % (
        9 - (sum(
            (3 - (i % 2) * 2) * int(barcode[-i-1])
            for i in range(0, len(barcode))
            ) + 9) % 10
        )


class FamiPortBarcodeNoSequence(Base):
    __tablename__ = 'FamiPortBarcodeNoSequence'

    id = sa.Column(Identifier, primary_key=True)

    @classmethod
    def get_next_value(cls, discrimination_code, session):
        seq = cls()
        session.add(seq)
        session.flush()
        barcode = u'1%d%011ld' % (
            discrimination_code,
            screw36(seq.id, 0x123456789L),
            )
        cd = calculate_gtin_cd(barcode)
        return barcode[1:] + cd


class FamiPortOrderIdentifierSequence(Base):
    __tablename__ = 'FamiPortOrderIdentifierSequence'

    id = sa.Column(Identifier, primary_key=True)
    prefix = sa.Column(sa.Unicode(3), nullable=False)

    @classmethod
    def get_next_value(cls, prefix, session):
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


class FamiPortExchangeTicketNoSequence(Base):
    __tablename__ = 'FamiPortExchangeTicketNoSequence'

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


class FamiPortReserveNumberSequence(Base):
    __tablename__ = 'FamiPortReserveNumberSequence'

    id = sa.Column(Identifier, primary_key=True)
    value = sa.Column(sa.String(13), nullable=False, unique=True)

    @classmethod
    def get_next_value(cls, famiport_client, session):
        for ii in range(15):  # retry count
            try:
                return cls._get_next_value(famiport_client, session)
            except InvalidRequestError:
                pass
        raise FamiPortNumberingError()

    @classmethod
    def _get_next_value(cls, famiport_client, session):
        seq = cls(value='%d%s' % (famiport_client.playguide.discrimination_code % 10, create_random_sequence_number(12)))
        session.add(seq)
        session.flush()
        return seq.value


class FamiPortOrder(Base, WithTimestamp):
    __tablename__ = 'FamiPortOrder'

    id                           = sa.Column(Identifier, primary_key=True, autoincrement=True)
    type                         = sa.Column(sa.Integer, nullable=False)
    order_no                     = sa.Column(sa.Unicode(12), nullable=False)
    famiport_order_identifier    = sa.Column(sa.Unicode(12), nullable=False, unique=True)  # 注文ID
    famiport_sales_segment_id    = sa.Column(Identifier, sa.ForeignKey('FamiPortSalesSegment.id'), nullable=True)
    famiport_performance_id      = sa.Column(Identifier, sa.ForeignKey('FamiPortPerformance.id'), nullable=False)
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

    ticketing_start_at = sa.Column(sa.DateTime(), nullable=True)
    ticketing_end_at = sa.Column(sa.DateTime(), nullable=True)
    payment_start_at = sa.Column(sa.DateTime(), nullable=True)
    payment_due_at = sa.Column(sa.DateTime(), nullable=True)

    customer_name = sa.Column(sa.Unicode(42), nullable=False)  # 氏名
    customer_name_input = sa.Column(sa.Boolean, nullable=False, default=0)  # 氏名要求フラグ
    customer_phone_input = sa.Column(sa.Boolean, nullable=False, default=0)  # 電話番号要求フラグ
    customer_address_1 = sa.Column(sa.Unicode(200), nullable=False, default=u'')  # 住所1
    customer_address_2 = sa.Column(sa.Unicode(200), nullable=False, default=u'')  # 住所2
    customer_phone_number = sa.Column(sa.Unicode(12), nullable=False)  # 電話番号

    report_generated_at          = sa.Column(sa.DateTime(), nullable=True)

    payment_sheet_text           = sa.Column(sa.Unicode(490), nullable=True)

    require_ticketing_fee_on_ticketing = sa.Column(sa.Boolean(), nullable=False, default=False)

    expired_at                   = sa.Column(sa.DateTime(), nullable=True)

    famiport_sales_segment = orm.relationship(
        'FamiPortSalesSegment',
        primaryjoin=lambda: FamiPortOrder.famiport_sales_segment_id == FamiPortSalesSegment.id
        )
    famiport_performance = orm.relationship(
        'FamiPortPerformance',
        primaryjoin=lambda: FamiPortOrder.famiport_performance_id == FamiPortPerformance.id,
        backref='orders'
        )
    famiport_client = orm.relationship('FamiPortClient')

    completed_famiport_receipts = orm.relationship(
        'FamiPortReceipt',
        primaryjoin=lambda: (FamiPortOrder.id == FamiPortReceipt.famiport_order_id) & (FamiPortReceipt.completed_at != None)
        )

    payment_famiport_receipt = orm.relationship(
        'FamiPortReceipt',
        uselist=False,
        primaryjoin=lambda: \
            (FamiPortOrder.id == FamiPortReceipt.famiport_order_id) & \
            FamiPortReceipt.is_payment_receipt & \
            (FamiPortReceipt.canceled_at == None)
        )

    ticketing_famiport_receipt = orm.relationship(
        'FamiPortReceipt',
        uselist=False,
        primaryjoin=lambda:\
            (FamiPortOrder.id == FamiPortReceipt.famiport_order_id) & \
            FamiPortReceipt.is_ticketing_receipt & \
            (FamiPortReceipt.canceled_at == None)
        )

    famiport_tickets = orm.relationship('FamiPortTicket', cascade='all,delete-orphan')

    @property
    def performance_start_at(self):
        return self.famiport_performance and self.famiport_performance.start_at

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

    def get_receipt(self, barcode_no):
        for receipt in self.famiport_receipts:
            if receipt.completed_at is None and barcode_no == receipt.barcode_no:
                return receipt

    @property
    def issuing_shop_code(self):
        for receipt in self.famiport_receipts:
            return receipt.shop_code
        return None

    @property
    def get_type_in_str(self):
        if self.type == FamiPortOrderType.CashOnDelivery.value:
            return u'代引'
        elif self.type == FamiPortOrderType.Payment.value:
            return u'前払い(後日渡し)'
        elif self.type == FamiPortOrderType.Ticketing.value:
            return u'代済'
        elif self.type == FamiPortOrderType.PaymentOnly.value:
            return u'前払いのみ'

    def mark_issued(self, now, request):
        if self.invalidated_at is not None:
            raise FamiPortUnsatisfiedPreconditionError('FamiPortOrder(id=%ld, order_no=%s) is already invalidated' % (self.id, self.order_no))
        if self.canceled_at is not None:
            raise FamiPortUnsatisfiedPreconditionError('FamiPortOrder(id=%ld, order_no=%s) is already canceled' % (self.id, self.order_no))
        if self.issued_at is not None:
            raise FamiPortUnsatisfiedPreconditionError('FamiPortOrder(id=%ld, order_no=%s) is already issued' % (self.id, self.order_no))
        logger.info('marking FamiPortOrder(id=%ld, order_no=%s) as issued' % (self.id, self.order_no))
        self.issued_at = now
        for famiport_ticket in self.famiport_tickets:
            famiport_ticket.issued_at = now

    def mark_paid(self, now, request):
        if self.invalidated_at is not None:
            raise FamiPortUnsatisfiedPreconditionError('FamiPortOrder(id=%ld, order_no=%s) is already invalidated' % (self.id, self.order_no))
        if self.canceled_at is not None:
            raise FamiPortUnsatisfiedPreconditionError('FamiPortOrder(id=%ld, order_no=%s) is already canceled' % (self.id, self.order_no))
        if self.paid_at is not None:
            # 再発券のケースがあるので例外にしない
            logger.warning('FamiPortOrder(id=%ld, order_no=%s) is already paid' % (self.id, self.order_no))
        logger.info('marking FamiPortOrder(id=%ld, order_no=%s) as paid' % (self.id, self.order_no))
        self.paid_at = now

    def can_cancel(self, now, request):
        if self.invalidated_at is not None:
            raise FamiPortUnsatisfiedPreconditionError('FamiPortOrder(id=%ld, order_no=%s) is already invalidated' % (self.id, self.order_no))
        if self.canceled_at is not None:
            raise FamiPortUnsatisfiedPreconditionError('FamiPortOrder(id=%ld, order_no=%s) is already canceled' % (self.id, self.order_no))
        if any(famiport_receipt.completed_at is not None and famiport_receipt.canceled_at is None for famiport_receipt in self.famiport_receipts):
            raise FamiPortUnsatisfiedPreconditionError('FamiPortOrder(id=%ld, order_no=%s) cannot be canceled; already paid / issued' % (self.id, self.order_no))
        if any(famiport_receipt.payment_request_received_at is not None and famiport_receipt.canceled_at is None for famiport_receipt in self.famiport_receipts):
            raise FamiPortUnsatisfiedPreconditionError('FamiPortOrder(id=%ld, order_no=%s) cannot be canceled; there are pending receipt(s)' % (self.id, self.order_no))
        # SEJの要件に平仄を取るために追加 tkt1009
        if self.type == FamiPortOrderType.Ticketing.value and self.ticketing_end_at < now:
            raise FamiPortUnsatisfiedPreconditionError('FamiPortOrder(id=%ld, order_no=%s) cannot be canceled; ticketing is overdue' % (self.id, self.order_no))

        return True

    def mark_canceled(self, now, request, cancel_reason_code=None, cancel_reason_text=None):
        if self.can_cancel(now, request):
            for famiport_receipt in self.famiport_receipts:
                if not famiport_receipt.canceled_at:
                    famiport_receipt.mark_canceled(now, request, cancel_reason_code=cancel_reason_code, cancel_reason_text=cancel_reason_text)
            logger.info('marking FamiPortOrder(id=%ld, order_no=%s) as canceled' % (self.id, self.order_no))
            self.canceled_at = now
            request.registry.notify(events.OrderCanceled(self, request))

    def mark_expired(self, now, request):
        logger.info('marking FamiPortOrder(id=%ld, order_no=%s) as expired' % (self.id, self.order_no))
        self.expired_at = now
        request.registry.notify(events.OrderExpired(self, request))

    def make_reissueable(self, now, request, cancel_reason_code=None, cancel_reason_text=None):
        if self.invalidated_at is not None:
            raise FamiPortUnsatisfiedPreconditionError(u'order is already invalidated')
        if self.canceled_at is not None:
            raise FamiPortUnsatisfiedPreconditionError(u'order is already canceled')
        if self.type == FamiPortOrderType.PaymentOnly.value:
            raise FamiPortUnsatisfiedPreconditionError(u'order is payment-only')
        ticketing_famiport_receipt = None
        for famiport_receipt in self.famiport_receipts:
            if famiport_receipt.type in (FamiPortReceiptType.CashOnDelivery.value, FamiPortReceiptType.Ticketing.value) and \
               famiport_receipt.canceled_at is None:
                assert ticketing_famiport_receipt is None
                ticketing_famiport_receipt = famiport_receipt
        if ticketing_famiport_receipt is not None:
            ticketing_famiport_receipt.mark_voided(now, request, FamiPortVoidReason.Reissuing.value, cancel_reason_code, cancel_reason_text)
            ticketing_famiport_receipt.make_reissueable(now, request)
            self.issued_at = None

    def make_suborder(self, now, request, type_=None, reason=None, cancel_reason_code=None, cancel_reason_text=None):
        if self.invalidated_at is not None:
            raise FamiPortUnsatisfiedPreconditionError(u'order is already invalidated')
        if self.canceled_at is not None:
            raise FamiPortUnsatisfiedPreconditionError(u'order is already canceled')
        # tkt1770: 支払期日を過ぎている場合は、同席番再予約は実施できないようにする
        if self.type != FamiPortOrderType.Ticketing.value and self.payment_due_at < now:
            raise FamiPortUnsatisfiedPreconditionError(u'cannot make suborder after payment due date passed.')
        for famiport_receipt in self.famiport_receipts:
            # 完了済みもしくはキャンセル済みでない場合に, レシートをキャンセルする
            if famiport_receipt.canceled_at is None and famiport_receipt.completed_at is None:
                famiport_receipt.mark_canceled(now, request, reason, cancel_reason_code, cancel_reason_text)

        if type_:
            logger.info("updated famiport_order.type to:{}".format(type_))
            self.type = type_
        self.add_receipts(suborder=True)

    def add_receipts(self, suborder=False):
        session = object_session(self)
        if self.type == FamiPortOrderType.Payment.value:
            # 同席番再予約経由用
            if suborder:
                # 支払済みの場合はレシートを作りなおさない
                if not self.paid_at:
                    self.famiport_receipts.append(
                    FamiPortReceipt.create(
                        session, self.famiport_client,
                        type=FamiPortReceiptType.Payment.value
                        ))
                # 発券済みの場合はレシートを作りなおさない
                if not self.issued_at:
                    self.famiport_receipts.append(
                    FamiPortReceipt.create(
                        session, self.famiport_client,
                        type=FamiPortReceiptType.Ticketing.value
                        ))
            else:
                self.famiport_receipts.extend([
                    FamiPortReceipt.create(
                      session, self.famiport_client,
                      type=FamiPortReceiptType.Payment.value
                    ),
                    FamiPortReceipt.create(
                      session, self.famiport_client,
                      type=FamiPortReceiptType.Ticketing.value
                    )
                ])
        else:
            if self.type == FamiPortOrderType.CashOnDelivery.value:
                receipt_type = FamiPortReceiptType.CashOnDelivery.value
            elif self.type in (FamiPortOrderType.Payment.value, FamiPortOrderType.PaymentOnly.value):
                receipt_type = FamiPortReceiptType.Payment.value
            elif self.type == FamiPortOrderType.Ticketing.value:
                receipt_type = FamiPortReceiptType.Ticketing.value
            else:
                raise AssertionError('never get here')
            self.famiport_receipts.append(
                FamiPortReceipt.create(
                    session, self.famiport_client,
                    type=receipt_type,
                    famiport_order_id=self.id
                    )
                )

    @property
    def automatically_cancellable(self):
        return self.invalidated_at is None and \
            self.canceled_at is None and \
            self.expired_at is None and \
            not any(
                famiport_receipt.canceled_at is None and famiport_receipt.completed_at is not None
                for famiport_receipt in self.famiport_receipts
                )

    def expired(self, now):
        if self.type == FamiPortOrderType.CashOnDelivery.value:
            if self.payment_famiport_receipt.completed_at is None:
                if self.payment_due_at < now or self.ticketing_end_at < now:
                    return self.payment_due_at
        elif self.type == FamiPortOrderType.Payment.value:
            if self.payment_famiport_receipt.completed_at is None:
                if self.payment_due_at < now:
                    return self.payment_due_at
            elif self.ticketing_famiport_receipt.completed_at is None:
                if self.ticketing_end_at < now:
                    return self.ticketing_end_at
        elif self.type == FamiPortOrderType.Ticketing.value:
            if self.ticketing_famiport_receipt.completed_at is None:
                if self.ticketing_end_at < now:
                    return self.ticketing_end_at
        elif self.type == FamiPortOrderType.PaymentOnly.value:
            if self.payment_famiport_receipt.completed_at is None:
                if self.payment_due_at < now:
                    return self.payment_due_at
        return None


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
    logically_subticket       = sa.Column(sa.Boolean, nullable=False, default=False)
    barcode_number            = sa.Column(sa.Unicode(13), nullable=False)
    template_code             = sa.Column(sa.Unicode(10), nullable=False)
    price                     = sa.Column(sa.Numeric(precision=9, scale=0), nullable=False, default=0)
    userside_id               = sa.Column(Identifier, nullable=True) # OrderedProductItemToken.serial
    userside_token_id         = sa.Column(Identifier, nullable=True) # OrderedProductItemToken.id
    data                      = sa.Column(sa.Unicode(4000), nullable=False)
    issued_at                 = sa.Column(sa.DateTime(), nullable=True)

    famiport_order = orm.relationship('FamiPortOrder')

    @property
    def is_subticket(self):
        return self.logically_subticket or \
               self.type in (FamiPortTicketType.ExtraTicket.value, FamiPortTicketType.ExtraTicketWithBarcode.value)


class FamiPortInformationMessage(Base, WithTimestamp):
    __tablename__ = 'FamiPortInformationMessage'
    __table_args__ = (
        sa.UniqueConstraint(
            'result_code', 'reserve_number', 'famiport_sales_segment_id',
            'event_code_1', 'event_code_2',
            'performance_code', 'sales_segment_code', 'client_code',
            name='ix_unique_famiport_information_message',
            ),
        )

    id = sa.Column(Identifier, primary_key=True)
    result_code = sa.Column(sa.Integer, nullable=False)
    message = sa.Column(sa.Unicode(length=1000), nullable=False, default=u'')
    reserve_number = sa.Column(sa.Unicode(13), nullable=True)  # 予約番号
    event_code_1 = sa.Column(sa.Unicode(6), nullable=True)
    event_code_2 = sa.Column(sa.Unicode(4), nullable=True)
    performance_code = sa.Column(sa.Unicode(3), nullable=True)
    sales_segment_code = sa.Column(sa.Unicode(3), nullable=True)  # 受付コード
    client_code = sa.Column(sa.Unicode(24), nullable=True)
    famiport_sales_segment_id = sa.Column(Identifier, sa.ForeignKey('FamiPortSalesSegment.id'), nullable=True)
    famiport_sales_segment = orm.relationship('FamiPortSalesSegment')

    @classmethod
    def get_message(cls, information_result_code, default_message, session):
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
    code = sa.Column(sa.Unicode(5), nullable=False, unique=True)
    company_code = sa.Column(sa.Unicode(4), nullable=False)
    company_name = sa.Column(sa.Unicode(40), nullable=False)
    district_code = sa.Column(sa.Unicode(1), nullable=True)
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
    open_at = sa.Column(sa.Unicode(4), nullable=False, default=u'')
    close_at = sa.Column(sa.Unicode(4), nullable=False, default=u'')
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

    @classmethod
    def get_by_code(cls, code, session):
        return session.query(FamiPortShop).filter_by(code = code).first()

class FamiPortReceipt(Base, WithTimestamp):
    __tablename__ = 'FamiPortReceipt'

    id = sa.Column(Identifier, primary_key=True)
    type = sa.Column(sa.Integer, nullable=False)
    famiport_order_identifier = sa.Column(sa.Unicode(12), nullable=False, unique=True)  # 注文ID
    reserve_number = sa.Column(sa.Unicode(13), nullable=True, unique=True)  # 予約番号
    inquired_at = sa.Column(sa.DateTime(), nullable=True)  # 予約照会が行われた日時
    payment_request_received_at = sa.Column(sa.DateTime(), nullable=True)  # 支払/発券要求が行われた日時
    customer_request_received_at = sa.Column(sa.DateTime(), nullable=True)  # 顧客情報照会が行われた日時
    completed_at = sa.Column(sa.DateTime(), nullable=True)  # 完了処理が行われた日時
    void_at = sa.Column(sa.DateTime(), nullable=True)
    canceled_at = sa.Column(sa.DateTime(), nullable=True)
    void_reason = sa.Column(sa.Integer, nullable=True)
    rescued_at = sa.Column(sa.DateTime(), nullable=True)  # 90分救済措置にて救済された時刻
    barcode_no = sa.Column(sa.Unicode(13), nullable=True, unique=True)  # 支払番号

    famiport_order_id = sa.Column(Identifier, sa.ForeignKey('FamiPortOrder.id'), nullable=False)
    famiport_order = orm.relationship('FamiPortOrder', backref='famiport_receipts')

    shop_code = sa.Column(sa.Unicode(6), nullable=False, default=u'')

    report_generated_at = sa.Column(sa.DateTime(), nullable=True)

    made_reissueable_at = sa.Column(sa.DateTime(), nullable=True)

    shop = orm.relationship('FamiPortShop', primaryjoin=FamiPortShop.code == shop_code, foreign_keys=FamiPortShop.code, uselist=False)

    attributes_ = orm.relationship('FamiPortReceiptAttribute', backref='famiport_receipt', collection_class=attribute_mapped_collection('name'), )
    attributes = association_proxy('attributes_', 'value', creator=lambda k, v: FamiPortReceiptAttribute(name=k, value=v))

    @property
    def cancel_reason_code(self):
        return self.attributes.get('cancel_reason_code')

    @cancel_reason_code.setter
    def cancel_reason_code(self, value):
        self.attributes['cancel_reason_code'] = value

    @property
    def cancel_reason_text(self):
        return self.attributes.get('cancel_reason_text')

    @cancel_reason_text.setter
    def cancel_reason_text(self, value):
        self.attributes['cancel_reason_text'] = value

    @hybrid_property
    def is_payment_receipt(self):
        return (self.type == FamiPortReceiptType.Payment.value) | \
               (self.type == FamiPortReceiptType.CashOnDelivery.value)

    @hybrid_property
    def is_ticketing_receipt(self):
        return (self.type == FamiPortReceiptType.Ticketing.value) | \
               (self.type == FamiPortReceiptType.CashOnDelivery.value)

    @property
    def get_issued_status_in_str(self):
        # 発券対象でない場合
        if self.type == FamiPortReceiptType.Payment.value:
            return u'-'
        else:
            if self.completed_at is not None and self.rescued_at is not None:
                return u'発券済み(90分確定)'
            elif self.payment_request_received_at is not None and self.famiport_order.issued_at is not None \
                    and self.rescued_at is None:
                return u'発券済み'
            elif self.payment_request_received_at is not None and self.famiport_order.issued_at is None:
                return u'発券確定待ち'
            elif self.payment_request_received_at is None or self.inquired_at is None:
                return u'発券待ち'
            else:
                return u'状態不正'

    @property
    def get_payment_status_in_str(self):
        # 入金対象でない場合
        if self.type == FamiPortReceiptType.Ticketing.value:
            return u'-'
        else:
            if self.completed_at is not None and self.rescued_at is not None:
                return u'入金済み(90分確定)'
            elif self.payment_request_received_at is not None and self.famiport_order.paid_at is not None \
                    and self.rescued_at is None:
                return u'入金済み'
            elif self.payment_request_received_at is not None and self.famiport_order.paid_at is None:
                return u'入金確定待ち'
            elif self.payment_request_received_at is None or self.inquired_at is None:
                return u'入金待ち'
            else:
                return u'状態不正'

    def get_shop_name(self, request):
        if self.payment_request_received_at:
            session = object_session(self)
            shop = session.query(FamiPortShop)\
                               .filter(FamiPortShop.code == self.shop_code)\
                               .first()
        else:
            return u"要求未済"

        return shop.name if shop else u'-'

    def can_payment(self, now):
        return self.inquired_at is not None\
            and (self.payment_request_received_at is None or self.payment_request_received_at < self.inquired_at) \
            and (self.completed_at is None or self.made_reissueable_at is not None)

    def can_completion(self, now):
        return self.inquired_at is not None \
            and self.payment_request_received_at is not None \
            and (self.completed_at is None or self.made_reissueable_at is not None)

    def can_rescue(self, now):
        return self.inquired_at is not None \
            and self.payment_request_received_at is not None \
            and self.completed_at is None \
            and self.rescued_at is None

    @classmethod
    def get_by_reserve_number(cls, reserve_number, session):
        return session \
            .query(cls) \
            .options(orm.joinedload(cls.famiport_order)) \
            .join(cls.famiport_order) \
            .filter(cls.reserve_number == reserve_number) \
            .filter(FamiPortOrder.invalidated_at.is_(None)) \
            .one()

    @classmethod
    def get_by_barcode_no(cls, barcode_no, session):
        return session \
            .query(cls) \
            .options(orm.joinedload(cls.famiport_order)) \
            .join(cls.famiport_order) \
            .filter(cls.barcode_no == barcode_no) \
            .filter(FamiPortOrder.invalidated_at.is_(None)) \
            .one()

    def mark_inquired(self, now, request):
        logger.info('marking FamiPortReceipt(id=%ld, reserve_number=%s) as inquired' % (self.id, self.reserve_number))
        self.inquired_at = now
        request.registry.notify(events.ReceiptInquired(self, request))

    def mark_payment_request_received(self, now, request):
        logger.info('marking FamiPortReceipt(id=%ld, reserve_number=%s) as payment_request_received' % (self.id, self.reserve_number))
        self.payment_request_received_at = now
        request.registry.notify(events.ReceiptPaymentRequestReceived(self, request))

    def mark_completed(self, now, request):
        logger.info('marking FamiPortReceipt(id=%ld, reserve_number=%s) as completed' % (self.id, self.reserve_number))
        if self.completed_at is not None:
            if self.made_reissueable_at is None:
                raise FamiPortUnsatisfiedPreconditionError('FamiPortReceipt(id=%ld, reserve_number=%s) is already completed' % (self.id, self.reserve_number))
            else:
                logger.info('FamiPortReceipt(id=%ld, reserve_number=%s) is marked reissueable' % (self.id, self.reserve_number))
        else:
            self.completed_at = now
        self.made_reissueable_at = None
        request.registry.notify(events.ReceiptCompleted(self, request))

    def mark_voided(self, now, request, reason=None, cancel_reason_code=None, cancel_reason_text=None):
        if self.void_at is not None:
            logger.info('FamiPortReceipt(id=%ld, reserve_number=%s) is already voided' % (self.id, self.reserve_number))
        logger.info('marking FamiPortReceipt(id=%ld, reserve_number=%s) as voided' % (self.id, self.reserve_number))
        self.void_at = now
        self.void_reason = reason
        self.payment_request_received_at = None
        self.made_reissueable_at = None
        self.cancel_reason_code = cancel_reason_code
        self.cancel_reason_text = cancel_reason_text
        request.registry.notify(events.ReceiptVoided(self, request))

    def mark_canceled(self, now, request, reason=None, cancel_reason_code=None, cancel_reason_text=None):
        if self.canceled_at is not None:
            raise FamiPortUnsatisfiedPreconditionError('FamiPortReceipt(id=%ld, reserve_number=%s) is already canceled' % (self.id, self.reserve_number))
        logger.info('marking FamiPortReceipt(id=%ld, reserve_number=%s) as canceled' % (self.id, self.reserve_number))
        self.canceled_at = now
        self.void_reason = reason
        self.cancel_reason_code = cancel_reason_code
        self.cancel_reason_text = cancel_reason_text
        request.registry.notify(events.ReceiptCanceled(self, request))

    def make_reissueable(self, now, request):
        logger.info('FamiPortReceipt(id=%ld).made_reissueable_at is set to %s' % (self.id, now))
        self.made_reissueable_at = now

    def calculate_total_and_fees(self):
        ticket_payment = Decimal(0)
        system_fee = Decimal(0)
        ticketing_fee = Decimal(0)
        famiport_order = self.famiport_order

        if self.type == FamiPortReceiptType.CashOnDelivery.value:
            ticket_payment = famiport_order.ticket_payment
            system_fee = famiport_order.system_fee
            ticketing_fee = famiport_order.ticketing_fee
        elif self.type == FamiPortReceiptType.Payment.value:
            ticket_payment = famiport_order.ticket_payment
            system_fee = famiport_order.system_fee
            if famiport_order.require_ticketing_fee_on_ticketing:
                ticketing_fee = Decimal(0)
            else:
                ticketing_fee = famiport_order.ticketing_fee
        elif self.type == FamiPortReceiptType.Ticketing.value:
            ticket_payment = Decimal(0)
            system_fee = Decimal(0)
            if famiport_order.require_ticketing_fee_on_ticketing:
                ticketing_fee = famiport_order.ticketing_fee
            else:
                ticketing_fee = Decimal(0)
        total_amount = ticket_payment + system_fee + ticketing_fee
        return total_amount, ticket_payment, system_fee, ticketing_fee

    @classmethod
    def create(cls, session, famiport_client, **kwargs):
        return FamiPortReceipt(
            reserve_number=FamiPortReserveNumberSequence.get_next_value(famiport_client, session),
            famiport_order_identifier=FamiPortOrderIdentifierSequence.get_next_value(famiport_client.prefix, session),
            **kwargs
            )


class FamiPortReceiptAttribute(Base):
    __tablename__ = 'FamiPortReceiptAttribute'
    __table_args__ = (
        sa.PrimaryKeyConstraint('famiport_receipt_id', 'name'),
        )
    famiport_receipt_id = sa.Column(Identifier, sa.ForeignKey('FamiPortReceipt.id'), nullable=False)
    name = sa.Column(sa.Unicode(64), nullable=False)
    value = sa.Column(sa.Unicode(1024), nullable=True)
