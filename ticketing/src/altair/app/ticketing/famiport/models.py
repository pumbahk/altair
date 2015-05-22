# -*- coding: utf-8 -*-
import types
import sqlalchemy as sa
from sqlalchemy.types import TypeDecorator
from sqlalchemy import orm
from sqlalchemy.ext.mutable import Mutable
import sqlahelper
from altair.models.nervous import NervousList
from altair.models import Identifier, WithTimestamp
from .utils import InformationResultCodeEnum
from enum import Enum

Base = sqlahelper.get_base()

# 内部トランザクション用
_session = orm.scoped_session(orm.sessionmaker())

class FamiPortOrderNoSequence(Base, WithTimestamp):
    __tablename__ = 'FamiPortOrderNoSequence'

    id = sa.Column(Identifier, primary_key=True)

    @classmethod
    def get_next_value(cls, name):
        seq = cls()
        _session.add(seq)
        _session.flush()
        return seq.id


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
    Fukushima  = (40, u'福岡県', FamiPortArea.KyushuOkinawa)
    Saga       = (41, u'佐賀県', FamiPortArea.KyushuOkinawa)
    Nagasaki   = (42, u'長崎県', FamiPortArea.KyushuOkinawa)
    Kumamoto   = (43, u'熊本県', FamiPortArea.KyushuOkinawa)
    Oita       = (44, u'大分県', FamiPortArea.KyushuOkinawa)
    Miyagi     = (45, u'宮城県', FamiPortArea.KyushuOkinawa)
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


class FamiPortClient(Base, WithTimestamp):
    __tablename__ = 'FamiPortClient'

    playguide_id = sa.Column(Identifier, sa.ForeignKey('FamiPortPlayguide.id'), nullable=False)
    code         = sa.Column(sa.Unicode(24), nullable=False, primary_key=True)

    playguide    = orm.relationship(FamiPortPlayguide)


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
    code_1                  = sa.Column(sa.Unicode(6), nullable=False) 
    code_2                  = sa.Column(sa.Unicode(4), nullable=False) 
    name_1                  = sa.Column(sa.Unicode(80), nullable=False, default=u'')
    name_2                  = sa.Column(sa.Unicode(80), nullable=False, default=u'')
    sales_channel           = sa.Column(sa.Integer, nullable=False, default=FamiPortSalesChannel.FamiPortOnly.value)
    client_code             = sa.Column(sa.Unicode(24), sa.ForeignKey('FamiPortClient.code'))
    venue_id                = sa.Column(Identifier, sa.ForeignKey('FamiPortVenue.id'))
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
    famiport_event_id       = sa.Column(Identifier, sa.ForeignKey('FamiPortEvent.id'), nullable=False)
    code                    = sa.Column(sa.Unicode(3))
    name                    = sa.Column(sa.Unicode(60))
    type                    = sa.Column(sa.Integer, nullable=False, default=FamiPortPerformanceType.Normal.value)
    searchable              = sa.Column(sa.Boolean, nullable=False, default=True)
    sales_channel           = sa.Column(sa.Integer, nullable=False, default=FamiPortSalesChannel.FamiPortOnly.value)
    start_at                = sa.Column(sa.DateTime(), nullable=True)
    ticket_name             = sa.Column(sa.Unicode(20), nullable=True) # only valid if type == Spanned

    famiport_event = orm.relationship('FamiPortEvent')


class FamiPortSalesSegment(Base, WithTimestamp):
    __tablename__ = 'FamiPortSalesSegment'

    id                      = sa.Column(Identifier, primary_key=True, autoincrement=True)
    famiport_performance_id = sa.Column(Identifier, sa.ForeignKey('FamiPortPerformance.id'), nullable=False)
    code                    = sa.Column(sa.Unicode(3), nullable=False)
    name                    = sa.Column(sa.Unicode(40), nullable=False)
    sales_channel           = sa.Column(sa.Integer, nullable=False, default=FamiPortSalesChannel.FamiPortOnly.value)
    published_at            = sa.Column(sa.DateTime(), nullable=True)
    start_at                = sa.Column(sa.DateTime(), nullable=False)
    end_at                  = sa.Column(sa.DateTime(), nullable=True)
    auth_required           = sa.Column(sa.Boolean, nullable=False, default=1)
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

    famiport_ticket = orm.relationship('FamiPortTicket')
    famiport_refund = orm.relationship('FamiPortRefund')


class FamiPortOrder(Base, WithTimestamp):
    __tablename__ = 'FamiPortOrder'

    id                        = sa.Column(Identifier, primary_key=True, autoincrement=True)
    fm_order_no               = sa.Column(sa.Unicode(12), nullable=False)
    shop_code                 = sa.Column(sa.Unicode(6), nullable=False)
    famiport_sales_segment_id = sa.Column(Identifier, sa.ForeignKey('FamiPortSalesSegment.id'))
    generation                = sa.Column(sa.Integer, nullable=False, default=0)
    invalidated_at            = sa.Column(sa.DateTime(), nullable=True)

    famiport_sales_segment = orm.relationship('FamiPortSalesSegment')


class FamiPortTicketType(Enum):
    Ticket                 = 2
    TicketWithBarcode      = 1
    ExtraTicket            = 4
    ExtraTicketWIthBarcode = 3


class FamiPortTicket(Base, WithTimestamp):
    __tablename__ = 'FamiPortTicket'

    id                        = sa.Column(Identifier, primary_key=True, autoincrement=True)
    famiport_order_id         = sa.Column(Identifier, sa.ForeignKey('FamiPortOrder.id'), nullable=False)
    type                      = sa.Column(sa.Integer, nullable=False, default=FamiPortTicketType.TicketWithBarcode.value)
    barcode_number            = sa.Column(sa.Unicode(13), nullable=False)
    template_code             = sa.Column(sa.Unicode(10), nullable=False)
    data                      = sa.Column(sa.Unicode(4000), nullable=False)
    issued_at                 = sa.Column(sa.DateTime(), nullable=False)

    famiport_order = orm.relationship('FamiPortOrder', backref='famiport_tickets')

class FamiPortInformationMessage(Base, WithTimestamp):
    __tablename__ = 'FamiPortInformationMessage'
    __table_args__= (sa.UniqueConstraint('result_code'),)

    id = sa.Column(Identifier, primary_key=True)
    result_code = sa.Column(sa.Enum('WithInformation', 'ServiceUnavailable'), unique=True, nullable=False)
    message = sa.Column(sa.Unicode(length=1000), nullable=True)

    @classmethod
    def create(cls, result_code, message):
        return cls(result_code=result_code, message=message)

    @classmethod
    def get_message(cls, information_result_code, default_message=None):
        if not isinstance(information_result_code, InformationResultCodeEnum):
            return None
        query = FamiPortInformationMessage.filter_by(result_code=information_result_code.name)
        famiport_information_message = query.first()
        if famiport_information_message:
            return famiport_information_message.message
        else:
            return default_message
