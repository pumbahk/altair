# -*- coding: utf-8 -*-

from altair.app.ticketing.models import BaseModel, LogicallyDeleted, WithTimestamp, MutationDict, JSONEncodedDict, Identifier
from sqlalchemy import Table, Column, BigInteger, Integer, String, DateTime, Date, ForeignKey, Enum, DECIMAL, Binary, UniqueConstraint
from sqlalchemy.orm import relationship, join, column_property, mapper, backref
from sqlalchemy.sql.expression import asc
import sqlahelper
from datetime import datetime
from altair.app.ticketing.utils import StandardEnum

session = sqlahelper.get_session()
Base = sqlahelper.get_base()

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
    return type != SejPaymentType.PrepaymentOnly

class SejTicketType(StandardEnum):
    # 1:本券(チケットバーコード有り)
    Ticket                  = 2
    # 2:本券(チケットバーコード無し)
    TicketWithBarcode       = 1
    # 3:本券以外(チケットバーコード有り)
    ExtraTicket             = 4
    # 4:本券以外(チケットバーコード無し)
    ExtraTicketWithBarcode  = 3

code_from_ticket_type = dict((enum_.v, enum_) for enum_ in SejTicketType)

def is_ticket(type):
    return type in (SejTicketType.Ticket, SejTicketType.TicketWithBarcode)

class SejOrderUpdateReason(StandardEnum):
    # 項目変更
    Change = 1
    # 公演中止
    Stop = 2

code_from_update_reason = dict((enum_.v, enum_) for enum_ in SejOrderUpdateReason)


class SejTenant(BaseModel,  WithTimestamp, LogicallyDeleted, Base):
    __tablename__           = 'SejTenant'
    id                      = Column(Identifier, primary_key=True)
    shop_name               = Column(String(12))
    shop_id                 = Column(String(12))
    contact_01              = Column(String(128))
    contact_02              = Column(String(255))
    api_key                 = Column(String(255), nullable=True)
    inticket_api_url        = Column(String(255), nullable=True)

    organization_id         = Column(Identifier) # あえてRelationしません


class SejTicketTemplateFile(BaseModel,  WithTimestamp, LogicallyDeleted, Base):
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


class SejRefundEvent(BaseModel,  WithTimestamp, LogicallyDeleted, Base):
    __tablename__           = 'SejRefundEvent'
    id                      = Column(Identifier, primary_key=True)
    available = Column(Integer)
    shop_id = Column(String(5))
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


class SejRefundTicket(BaseModel,  WithTimestamp, LogicallyDeleted, Base):
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
    sent_at = Column(DateTime, nullable=True)


class SejFile(BaseModel, WithTimestamp, LogicallyDeleted, Base):
    __tablename__           = 'SejFile'
    id                      = Column(Identifier, primary_key=True)
    notification_type       = Column(Enum('91', '51', '61', '92', '94', '95', '96'))
    file_date               = Column(Date, unique=True)
    reflected_at            = Column(DateTime, nullable=True)
    file_url                = Column(String(255))


class SejOrder(BaseModel,  WithTimestamp, LogicallyDeleted, Base):
    __tablename__           = 'SejOrder'
    __table_args__= (
        UniqueConstraint('order_no', 'branch_no'),
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

    # 枝番 (もとい、バージョン番号. 1スタートで1づつ単調増加)
    # Order.branch_no とは直接関係ない。再付番の際に増える
    branch_no               = Column(Integer, nullable=False, default=1, server_default='1')

    def mark_canceled(self, now=None):
        self.cancel_at = now or datetime.now() # SAFE TO USE datetime.now() HERE

    def mark_issued(self, now=None):
        self.issue_at = now or datetime.now() # SAFE TO USE datetime.now() HERE

    def mark_paid(self, now=None):
        self.pay_at = now or datetime.now() # SAFE TO USE datetime.now() HERE

    @property
    def prev(self):
        return DBSession.query(self.__class__, include_deleted=True) \
            .filter_by(order_no=self.order_no, branch_no=(self.branch_no - 1)) \
            .one()

    @property
    def next(self):
        return DBSession.query(self.__class__, include_deleted=True) \
            .filter_by(order_no=self.order_no, branch_no=(self.branch_no + 1)) \
            .one()

    @property
    def tickets(self):
        return SejTicket.query.filter_by(sej_order_id=self.id).order_by(SejTicket.ticket_idx).all()

    def new_branch(self, payment_type, ticketing_due_at, exchange_number=None, billing_number=None, processed_at=None):
        # payment_type は文字列になり得る (MySQLのENUM型をDBAPIは文字列として扱う)
        if int(payment_type) == SejPaymentType.Paid:
            # 再付番の際、代済に変更になるということは、必ず支払済のはずのため
            # (これはSEJ側の想定)、payment_due_atは変更してはならない
            payment_due_at_new = self.payment_due_at
        else:
            # 代引の場合は payment_due_at は ticketing_due_at と必ず等しくなるはずである
            payment_due_at_new = ticketing_due_at
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
            branch_no=(self.branch_no + 1),
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
            ticketing_start_at=self.ticketing_start_at,
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
    def branches(cls, order_no):
        return cls.query.filter_by(order_no=order_no).order_by(asc(cls.branch_no)).all()

class SejTicket(BaseModel,  WithTimestamp, LogicallyDeleted, Base):
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
    order                   = relationship("SejOrder", primaryjoin='SejOrder.id==SejTicket.sej_order_id', foreign_keys=[sej_order_id])
    order_no                = Column(String(12), ForeignKey("SejOrder.order_no"), nullable=True)
    ticket_idx              = Column(Integer)
    product_item_id         = Column(Identifier, ForeignKey("ProductItem.id"), nullable=True)

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

from .notification.models import *
