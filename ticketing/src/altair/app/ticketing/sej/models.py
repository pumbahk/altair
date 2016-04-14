# -*- coding: utf-8 -*-

from sqlalchemy.sql import func
from altair.models import LogicallyDeleted, WithTimestamp, Identifier
from sqlalchemy import Table, Column, BigInteger, Integer, String, DateTime, Date, ForeignKey, Enum, DECIMAL, Binary, UniqueConstraint, Unicode
from sqlalchemy.orm import relationship, join, column_property, mapper, backref, scoped_session, sessionmaker
from sqlalchemy.orm.session import object_session
from sqlalchemy.sql.expression import asc, desc
from zope.interface import implementer
import sqlahelper
from datetime import datetime
from altair.app.ticketing.utils import StandardEnum
from .interfaces import ISejTenant, ISejTicketTemplateRecord

Base = sqlahelper.get_base()

# 内部トランザクション用
_session = scoped_session(sessionmaker())

class SejPaymentType(StandardEnum):
    # 01:代引き
    CashOnDelivery  = 1
    # 02:前払い(後日発券)
    Prepayment      = 2
    # 03:代済発券
    Paid            = 3
    # 04:前払いのみ
    PrepaymentOnly  = 4

code_from_payment_type = dict((enum_.v, enum_) for enum_ in SejPaymentType)

def need_ticketing(type):
    return int(type) != int(SejPaymentType.PrepaymentOnly)

class SejTicketType(StandardEnum):
    # 1:本券(チケットバーコード有り)
    TicketWithBarcode       = 1
    # 2:本券(チケットバーコード無し)
    Ticket                  = 2
    # 3:本券以外(チケットバーコード有り)
    ExtraTicketWithBarcode  = 3
    # 4:本券以外(チケットバーコード無し)
    ExtraTicket             = 4

code_from_ticket_type = dict((enum_.v, enum_) for enum_ in SejTicketType)

def is_ticket(type):
    return type in (SejTicketType.Ticket, SejTicketType.TicketWithBarcode)

class SejOrderUpdateReason(StandardEnum):
    # 項目変更
    Change = 1
    # 公演中止
    Stop = 2

code_from_update_reason = dict((enum_.v, enum_) for enum_ in SejOrderUpdateReason)

@implementer(ISejTicketTemplateRecord)
class SejTicketTemplateFile(Base, WithTimestamp, LogicallyDeleted):
    __tablename__           = 'SejTicketTemplateFile'
    id                      = Column(Identifier, primary_key=True)
    status                  = Column(Enum('1', '2', '3', '4'))
    template_id             = Column(String(200))
    template_name           = Column(String(36))
    ticket_html             = Column(Binary)
    ticket_css              = Column(Binary)
    publish_start_date      = Column(Date)
    publish_end_date        = Column(Date)
    sent_at                 = Column(DateTime)
    notation_version        = Column(Integer, nullable=False)


class SejRefundEvent(Base, WithTimestamp, LogicallyDeleted):
    __tablename__           = 'SejRefundEvent'
    id                      = Column(Identifier, primary_key=True)
    available               = Column(Integer)
    shop_id                 = Column(String(5))
    nwts_endpoint_url       = Column(String(255), nullable=True)
    nwts_terminal_id        = Column(String(255), nullable=True)
    nwts_password           = Column(String(255), nullable=True)
    event_code_01  = Column(String(16))
    event_code_02  = Column(String(16), nullable=True)
    title = Column(String(200))
    sub_title = Column(String(600), nullable=True)
    event_at = Column(DateTime)
    start_at = Column(DateTime) #レジ払戻受付開始日
    end_at = Column(DateTime) #レジ払戻受付終了日
    event_expire_at = Column(DateTime) #公演レコード有効期限
    ticket_expire_at = Column(DateTime) #チケット持ち込み期限
    refund_enabled = Column(Integer) # レジ払戻可能フラグ
    disapproval_reason = Column(Integer) # 払戻不可理由 2固定 半角[0-9]
    need_stub = Column(Integer) # 半券要否区分
    remarks = Column(String(256)) #備考
    un_use_01 = Column(String(64))
    un_use_02 = Column(String(64))
    un_use_03 = Column(String(64))
    un_use_04 = Column(String(64))
    un_use_05 = Column(String(64))
    sent_at = Column(DateTime, nullable=True)


class SejRefundTicket(Base, WithTimestamp, LogicallyDeleted):
    __tablename__               = 'SejRefundTicket'
    id                          = Column(Identifier, primary_key=True)
    refund_event_id             = Column(Identifier, ForeignKey("SejRefundEvent.id"), nullable=True)
    refund_event                = relationship("SejRefundEvent", backref='tickets')
    available                   = Column(Integer)
    event_code_01               = Column(String(16))
    event_code_02               = Column(String(16), nullable=True)
    order_no                    = Column(String(12))
    ticket_barcode_number       = Column(String(13))
    refund_ticket_amount        = Column(DECIMAL)
    refund_other_amount         = Column(DECIMAL)
    sent_at                     = Column(DateTime, nullable=True)
    refunded_at                 = Column(DateTime, nullable=True)
    status                      = Column(Integer)


class SejFile(Base, WithTimestamp, LogicallyDeleted):
    __tablename__           = 'SejFile'
    id                      = Column(Identifier, primary_key=True)
    notification_type       = Column(Enum('91', '51', '61', '92', '94', '95', '96'))
    file_date               = Column(Date, unique=True)
    reflected_at            = Column(DateTime, nullable=True)
    file_url                = Column(String(255))


class SejOrder(Base, WithTimestamp, LogicallyDeleted):
    __tablename__           = 'SejOrder'
    __table_args__= (
        UniqueConstraint('order_no', 'version_no', 'branch_no'),
        )
    id                      = Column(Identifier, primary_key=True)
    shop_id                 = Column(String(5))
    shop_name               = Column(String(64))
    contact_01              = Column(String(64))
    contact_02              = Column(String(64))
    user_name               = Column(String(40))
    user_name_kana          = Column(String(40))
    tel                     = Column(String(12))
    zip_code                = Column(String(7))
    email                   = Column(String(64))

    order_no                = Column(String(12))
    exchange_number         = Column(String(13))
    billing_number          = Column(String(13))

    exchange_sheet_url      = Column(String(128))
    exchange_sheet_number   = Column(String(32))

    total_price             = Column(DECIMAL)
    ticket_price            = Column(DECIMAL)
    commission_fee          = Column(DECIMAL)
    ticketing_fee           = Column(DECIMAL)

    total_ticket_count      = Column(Integer)
    ticket_count            = Column(Integer)
    return_ticket_count     = Column(Integer)

    process_id              = Column(String(12))
    payment_type            = Column(Enum('1', '2', '3', '4'))

    pay_store_number        = Column(String(6))
    pay_store_name          = Column(String(36))

    cancel_reason           = Column(String(2))

    ticketing_store_number  = Column(String(6))
    ticketing_store_name    = Column(String(36))

    payment_due_at          = Column(DateTime, nullable=True)
    ticketing_start_at      = Column(DateTime, nullable=True)
    ticketing_due_at        = Column(DateTime, nullable=True)
    regrant_number_due_at   = Column(DateTime, nullable=True)

    processed_at            = Column(DateTime, nullable=True)

    # 決済日時
    order_at                = Column(DateTime, nullable=True)
    # 支払日時
    pay_at                  = Column(DateTime, nullable=True)
    # 発券日時
    issue_at                = Column(DateTime, nullable=True)
    # キャンセル日時
    cancel_at               = Column(DateTime, nullable=True)

    # 枝番 (もとい、リビジョン番号. 1スタートで1づつ単調増加)
    # Order.branch_no とは直接関係ない。再付番の際に増える
    branch_no               = Column(Integer, nullable=False, default=1, server_default='1')


    # バージョン番号 (0スタートで1づつ単調増加)
    # 同じ order_no で注文を何個も作れるので、その区別に使う
    version_no              = Column(Integer, nullable=False, default=0, server_default='0')

    error_type              = Column(Integer, nullable=True)

    def mark_canceled(self, now=None):
        self.cancel_at = now or datetime.now() # SAFE TO USE datetime.now() HERE

    def mark_issued(self, now=None):
        self.issue_at = now or datetime.now() # SAFE TO USE datetime.now() HERE

    def mark_paid(self, now=None):
        self.pay_at = now or datetime.now() # SAFE TO USE datetime.now() HERE

    @property
    def prev(self):
        return object_session(self).query(self.__class__, include_deleted=True) \
            .filter_by(order_no=self.order_no, branch_no=(self.branch_no - 1)) \
            .one()

    @property
    def next(self):
        return object_session(self).query(self.__class__, include_deleted=True) \
            .filter_by(order_no=self.order_no, branch_no=(self.branch_no + 1)) \
            .one()

    @property
    def refund_tickets(self):
        return object_session(self).query(SejRefundTicket).filter_by(order_no=self.order_no).all()

    @property
    def refunded_tickets(self):
        return object_session(self).query(SejRefundTicket).filter(SejRefundTicket.order_no==self.order_no, SejRefundTicket.refunded_at!=None).all()

    @property
    def refunded_total_amount(self):
        return object_session(self).query(SejRefundTicket).filter(
            SejRefundTicket.order_no==self.order_no,
            SejRefundTicket.refunded_at!=None,
            SejRefundTicket.status==1
            ).with_entities(func.sum(SejRefundTicket.refund_ticket_amount + SejRefundTicket.refund_other_amount)).scalar() or 0

    def new_branch(self, payment_type=None, ticketing_start_at=None, ticketing_due_at=None, exchange_number=None, billing_number=None, processed_at=None):
        if payment_type is None: 
            payment_type = int(self.payment_type)
        if ticketing_due_at is None:
            ticketing_due_at = self.ticketing_due_at
        if ticketing_start_at is None:
            ticketing_start_at = self.ticketing_start_at

        # 最新の branch_no を取得する
        newest_one = object_session(self).query(self.__class__) \
            .filter_by(order_no=self.order_no) \
            .order_by(desc(self.__class__.branch_no)) \
            .first()

        assert newest_one is not None
        branch_no = newest_one.branch_no

        # payment_type は文字列になり得る (MySQLのENUM型をDBAPIは文字列として扱う)
        if int(payment_type) == int(SejPaymentType.Paid):
            # 再付番の際、代済に変更になるということは、必ず支払済のはずのため
            # (これはSEJ側の想定)、payment_due_atは変更してはならない
            payment_due_at_new = self.payment_due_at
        elif int(payment_type) == int(SejPaymentType.CashOnDelivery):
            # 代引の場合は payment_due_at は ticketing_due_at と必ず等しくなるはずである
            payment_due_at_new = ticketing_due_at or self.payment_due_at
        elif int(payment_type) == int(SejPaymentType.Prepayment):
            # 前払後日発券
            payment_due_at_new = self.payment_due_at
        elif int(payment_type) == int(SejPaymentType.PrepaymentOnly):
            # 前払のみ
            payment_due_at_new = self.payment_due_at
            ticketing_due_at = None

        return self.__class__(
            shop_id=self.shop_id,
            shop_name=self.shop_name,
            contact_01=self.contact_01,
            contact_02=self.contact_02,
            user_name=self.user_name,
            user_name_kana=self.user_name_kana,
            tel=self.tel,
            zip_code=self.zip_code,
            email=self.email,
            order_no=self.order_no,
            branch_no=(branch_no + 1),
            exchange_sheet_url=self.exchange_sheet_url,
            exchange_sheet_number=self.exchange_sheet_number,
            total_price=self.total_price,
            ticket_price=self.ticket_price,
            commission_fee=self.commission_fee,
            ticketing_fee=self.ticketing_fee,
            total_ticket_count=self.total_ticket_count,
            ticket_count=self.ticket_count,
            return_ticket_count=self.return_ticket_count,
            process_id=self.process_id,
            pay_store_number=self.pay_store_number,
            pay_store_name=self.pay_store_name,
            cancel_reason=self.cancel_reason,
            ticketing_store_number=self.ticketing_store_number,
            ticketing_store_name=self.ticketing_store_name,
            ticketing_start_at=ticketing_start_at,
            regrant_number_due_at=self.regrant_number_due_at,
            order_at=self.order_at,
            pay_at=self.pay_at,
            issue_at=self.issue_at,
            cancel_at=self.cancel_at,

            payment_type=payment_type,
            ticketing_due_at=ticketing_due_at,
            payment_due_at=payment_due_at_new,
            exchange_number=exchange_number or self.exchange_number,
            billing_number=billing_number or self.billing_number,
            processed_at=processed_at
            )

    @classmethod
    def branches(cls, order_no, session=_session):
        return session.query(cls).filter_by(order_no=order_no).order_by(asc(cls.branch_no)).all()

    @property
    def payment_and_delivery_done_at_once(self):
        return int(self.payment_type) == int(SejPaymentType.CashOnDelivery)


class SejTicket(Base, WithTimestamp, LogicallyDeleted):
    __tablename__           = 'SejTicket'

    id                      = Column(Identifier, primary_key=True)
    ticket_type             = Column(Enum('1', '2', '3', '4'))
    barcode_number          = Column(String(13))
    event_name              = Column(String(40))
    performance_name        = Column(String(40))
    performance_datetime    = Column(DateTime)
    ticket_template_id      = Column(String(10))
    ticket_data_xml         = Column(String(5000))
    sej_order_id            = Column(Identifier, ForeignKey("SejOrder.id"), nullable=False)
    order                   = relationship("SejOrder", primaryjoin='SejOrder.id==SejTicket.sej_order_id', foreign_keys=[sej_order_id], backref='tickets')
    order_no                = Column(String(12), ForeignKey("SejOrder.order_no"), nullable=True)
    ticket_idx              = Column(Integer)
    product_item_id         = Column(Identifier, ForeignKey("ProductItem.id"), nullable=True)
    ordered_product_item_token_id = Column(Identifier, ForeignKey("OrderedProductItemToken.id"), nullable=True)
    ordered_product_item_token    = relationship("OrderedProductItemToken")

    def new_branch(self, **kwargs):
        values = dict(
            ticket_type=self.ticket_type,
            barcode_number=self.barcode_number,
            event_name=self.event_name,
            performance_name=self.performance_name,
            performance_datetime=self.performance_datetime,
            ticket_template_id=self.ticket_template_id,
            ticket_data_xml=self.ticket_data_xml,
            order=self.order,
            order_no=self.order_no,
            ticket_idx=self.ticket_idx,
            product_item_id=self.product_item_id
            )
        values.update(kwargs)
        return self.__class__(**values)


@implementer(ISejTenant)
class ThinSejTenant(object):
    __slots__ = (
        '_shop_name',
        '_shop_id',
        '_contact_01',
        '_contact_02',
        '_api_key',
        '_inticket_api_url',
        '_nwts_endpoint_url',
        '_nwts_terminal_id',
        '_nwts_password',
        )

    @property
    def shop_name(self):
        return self._shop_name

    @property
    def shop_id(self):
        return self._shop_id

    @property
    def contact_01(self):
        return self._contact_01

    @property
    def contact_02(self):
        return self._contact_02

    @property
    def api_key(self):
        return self._api_key

    @property
    def inticket_api_url(self):
        return self._inticket_api_url

    @property
    def nwts_endpoint_url(self):
        return self._nwts_endpoint_url

    @property
    def nwts_terminal_id(self):
        return self._nwts_terminal_id

    @property
    def nwts_password(self):
        return self._nwts_password

    def __init__(self, original=None, shop_name=None, shop_id=None, contact_01=None, contact_02=None, api_key=None, inticket_api_url=None, nwts_endpoint_url=None, nwts_terminal_id=None, nwts_password=None):
        self._shop_name = shop_name if shop_name is not None else (original and original.shop_name)
        self._shop_id = shop_id if shop_id is not None else (original and original.shop_id)
        self._contact_01 = contact_01 if contact_01 is not None else (original and original.contact_01)
        self._contact_02 = contact_02 if contact_02 is not None else (original and original.contact_02)
        self._api_key = api_key if api_key is not None else (original and original.api_key)
        self._inticket_api_url = inticket_api_url if inticket_api_url is not None else (original and original.inticket_api_url)
        self._nwts_endpoint_url = nwts_endpoint_url if nwts_endpoint_url is not None else (original and original.nwts_endpoint_url)
        self._nwts_terminal_id = nwts_terminal_id if nwts_terminal_id is not None else (original and original.nwts_terminal_id)
        self._nwts_password = nwts_password if nwts_password is not None else (original and original.nwts_password)
