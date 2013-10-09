# coding: utf-8
import sqlahelper
from sqlalchemy import Table, Column, BigInteger, Integer, String, DateTime, Date, ForeignKey, Enum, DECIMAL, Binary, UniqueConstraint
from standardenum import StandardEnum

from altair.app.ticketing.models import BaseModel, LogicallyDeleted, WithTimestamp, MutationDict, JSONEncodedDict, relationship, Identifier

__all__ = [
    'SejNotificationType',
    'SejNotification',
    'code_from_notification_type',
    ]

Base = sqlahelper.get_base()

class SejNotificationType(StandardEnum):
    # '01':入金発券完了通知
    PaymentComplete = 1
    # '31':SVC強制取消通知
    CancelFromSVC = 31
    # '72':再付番通知
    ReGrant = 72
    # '73':発券期限切れ
    TicketingExpire = 73
    # 91
    InstantPaymentInfo = 91

    # 5-1.入金速報
    FileInstantPaymentInfo  = 94
    # 5-2.支払期限切れ
    FilePaymentExpire       = 51
    # 5-3.発券期限切れ
    FileTicketingExpire     = 61
    # 5-4.払戻速報
    FileInstantRefundInfo   = 92
    # 6-1.支払い案内
    FileCheckInfo           = 94
    # 6-2.会計取消(入金)
    FilePaymentCancel       = 95
    # 6-3.会計取消(発券)
    FileTicketingCancel     = 96
    # 6-4.払戻確定
    FileRefundComplete      = 97
    # 6-5.会計取消(発券)
    FileRefundCancel        = 98

code_from_notification_type = dict((enum_.v, enum_) for enum_ in SejNotificationType)

class SejNotification(BaseModel, WithTimestamp, LogicallyDeleted, Base):
    __tablename__           = 'SejNotification'

    id                      = Column(Identifier, primary_key=True)

    notification_type       = Column(Enum('1', '31', '72', '73'))
    process_number          = Column(String(12), index=True, unique=True)
    payment_type            = Column(Enum('1', '2', '3', '4'))
    payment_type_new        = Column(Enum('1', '2', '3', '4'), nullable=True)

    shop_id                 = Column(String(5))
    order_no                = Column(String(12))

    exchange_number         = Column(String(13))
    exchange_number_new     = Column(String(13), nullable=True)
    billing_number          = Column(String(13))
    billing_number_new      = Column(String(13), nullable=True)

    exchange_sheet_url      = Column(String(128), nullable=True)
    exchange_sheet_number   = Column(String(32), nullable=True)

    total_price             = Column(DECIMAL)
    total_ticket_count      = Column(Integer)

    ticket_count            = Column(Integer)
    return_ticket_count     = Column(Integer)

    ticketing_due_at        = Column(DateTime, nullable=True)
    ticketing_due_at_new    = Column(DateTime, nullable=True)

    pay_store_number        = Column(String(6))
    pay_store_name          = Column(String(36))

    ticketing_store_number  = Column(String(6))
    ticketing_store_name    = Column(String(36))

    cancel_reason           = Column(String(2), nullable=True)

    barcode_numbers         = Column(MutationDict.as_mutable(JSONEncodedDict(4096)), nullable=True)

    reflected_at            = Column(DateTime, nullable=True)
    processed_at            = Column(DateTime, nullable=True)

    signature               = Column(String(32))



