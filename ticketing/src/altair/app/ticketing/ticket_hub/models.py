# -*- coding: utf-8 -*-

from altair.models import LogicallyDeleted, WithTimestamp, Identifier
from sqlalchemy import Column, String, UniqueConstraint, ForeignKey, DateTime, Binary, Unicode
from sqlalchemy.orm import relationship, backref
import sqlahelper
import transaction
from datetime import datetime
from datetime import timedelta
from altair.ticket_hub.exc import TicketHubAPIError

Base = sqlahelper.get_base()
DBSession = sqlahelper.get_session()

class TicketHubCompletionError(Exception):
    def __init__(self, message, nested_exc_info=None):
        super(TicketHubCompletionError, self).__init__(message, nested_exc_info)

    @property
    def message(self):
        return self.args[0]

    @property
    def path(self):
        return self.args[1]

class TicketHubFacility(Base, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'TicketHubFacility'
    __table_args__ = (
        UniqueConstraint('code'),
    )
    id = Column(Identifier, primary_key=True)
    code = Column(String(5))
    # XXX: maybe should define in the config file
    agent_code = Column(String(4))

class TicketHubItemGroup(Base, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'TicketHubItemGroup'
    __table_args__ = (
        UniqueConstraint('code'),
    )
    id = Column(Identifier, primary_key=True)
    code = Column(String(4))
    ticket_hub_facility_id = Column(Identifier, ForeignKey("TicketHubFacility.id"), nullable=False)
    ticket_hub_facility = relationship("TicketHubFacility", backref='item_groups', uselist=False)

class TicketHubItem(Base, WithTimestamp, LogicallyDeleted):
    """
    Productに相当するTicketHub側のモデル
    引取方法がTICKET_HUB_DELIVERY_PLUGINな販売区分の商品に必ず対として必要なモデル
    TODO: 現状商品を管理画面で登録後、手でデータを作成する必要がある。管理画面から作成できるように改修が必要
    """
    __tablename__ = 'TicketHubItem'
    __table_args__ = (
        UniqueConstraint('code'),
    )
    id = Column(Identifier, primary_key=True)
    code = Column(String(5))
    ticket_hub_item_group_id = Column(Identifier, ForeignKey("TicketHubItemGroup.id"), nullable=False)
    ticket_hub_item_group = relationship("TicketHubItemGroup", primaryjoin='TicketHubItemGroup.id==TicketHubItem.ticket_hub_item_group_id', foreign_keys=[ticket_hub_item_group_id], backref='items')
    product_id = Column(Identifier, ForeignKey("Product.id"), nullable=False)
    product = relationship("Product", backref=backref('ticket_hub_item', uselist=False))

    @property
    def facility(self):
        self.ticket_hub_item_group.ticket_hub_facility

# XXX: Orderと別タイミングで生成できるのなら分けていた方が良い
# 現状のつくりだと、決済引取方法(及びshipping)を選択後でないと引取方法が確定しないので、Cartを作成する意味が薄い..
#
# class TicketHubCart(Base, WithTimestamp, LogicallyDeleted):
#     __tablename__ = 'TicketHubTempOrder'
#     __table_args__ = (
#         UniqueConstraint('cart_no'),
#     )
#     id = Column(Identifier, primary_key=True)
#     cart_no = Column(String(5))

class TicketHubOrder(Base, WithTimestamp, LogicallyDeleted):
    """
    Order(Cart)に相当するTicketHub側のモデル
    状態： カート(一時的に在庫確保) → 仮注文(決済まで完了済み。キャンセル可) → 注文確定(入場可。キャンセル不可)
    入場はTicketHubOrderedTicket.qr_codeを使用
    """
    __tablename__ = 'TicketHubOrder'
    __table_args__ = (
        UniqueConstraint('order_no'),
        )
    id = Column(Identifier, primary_key=True)
    altair_order_no = Column(Unicode(255), ForeignKey("Order.order_no"), nullable=False)
    order = relationship("Order", backref=backref('ticket_hub_order', uselist=False))
    cart_no = Column(String(36), nullable=False)
    order_no = Column(String(20), nullable=False)
    purchase_no = Column(String(30), nullable=False)
    purchase_qr_code = Column(String(41), nullable=False)
    total_amount = Column(String(8), nullable=False)
    total_ticket_quantity = Column(String(8), nullable=False)
    requested_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    canceled_at = Column(DateTime, nullable=True)

    @classmethod
    def create_from_temp_res(cls, ticket_hub_temp_order_res, ticket_hub_cart_res, cart):
        model = cls(
            altair_order_no=cart.order_no,
            cart_no=ticket_hub_cart_res.cart_id,
            order_no=ticket_hub_temp_order_res.order_no,
            purchase_no=ticket_hub_temp_order_res.purchase_no,
            purchase_qr_code=ticket_hub_temp_order_res.purchase_qr_code,
            total_amount=ticket_hub_temp_order_res.total_amount,
            total_ticket_quantity=ticket_hub_temp_order_res.total_ticket_quantity,
            requested_at=ticket_hub_temp_order_res.requested_at,
            tickets=TicketHubOrderedTicket.build_ticket_hub_ordered_tickets(ticket_hub_temp_order_res)
        )
        DBSession.add(model)
        return model

    def complete(self, api):
        try:
            res = api.complete_order(self.order_no)
        except TicketHubAPIError as e:
            raise e
        for response_set_key, response_set in res.res_dict.items():
            if response_set_key == 'response_set':
                for body_key, body in response_set.items():
                    if body_key == 'body':
                        for group in body['item_group_info_list']['item_group_info']:
                            for item in group['item_info_list']['item_info']:
                                for ticket in item['ticket_info_list']['ticket_info']:
                                    TicketHubOrderedTicket.update_usage_valid_date(
                                        get_value_from_ticket(ticket, 'disp_ticket_id'),
                                        get_value_from_ticket(ticket, 'usage_valid_start_date'),
                                        get_value_from_ticket(ticket, 'usage_valid_end_date'))
        self.completed_at = datetime.now()
        transaction.commit()
        return res


def get_value_from_ticket(ticket, key):
    return ticket[key] if key in ticket else None


def convert_datetime(date, days=0, seconds=0):
    if date is None:
        return None
    try:
        return datetime.strptime(date, '%Y%m%d') + timedelta(days=days, seconds=seconds)
    except (TypeError, ValueError):
        return None


class TicketHubOrderedTicket(Base, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'TicketHubOrderedTicket'
    id = Column(Identifier, primary_key=True)
    ticket_hub_order_id = Column(Identifier, ForeignKey("TicketHubOrder.id"), nullable=False)
    ticket_hub_order = relationship("TicketHubOrder", backref='tickets', uselist=False)
    qr_code = Column(String(41))
    qr_binary = Column(Binary)
    display_ticket_id = Column(String(30))
    usage_valid_start_date = Column(DateTime, nullable=True)
    usage_valid_end_date = Column(DateTime, nullable=True)

    @classmethod
    def from_res(cls, ticket_hub_ticket_res):
        return cls(
            qr_code=ticket_hub_ticket_res.ticket_qr_code,
            qr_binary=ticket_hub_ticket_res.ticket_qr_binary.encode('utf-8'),
            display_ticket_id=ticket_hub_ticket_res.ticket_id
        )

    @classmethod
    def build_ticket_hub_ordered_tickets(cls, order_res):
        return [cls.from_res(t) for t in order_res.tickets]

    @classmethod
    def update_usage_valid_date(cls, disp_ticket_id, start_date, end_date):
        if disp_ticket_id is not None:
            ticket = DBSession.query(TicketHubOrderedTicket)\
                .filter(TicketHubOrderedTicket.display_ticket_id == disp_ticket_id).first()
            ticket.usage_valid_start_date = convert_datetime(start_date)
            ticket.usage_valid_end_date = convert_datetime(end_date, days=1, seconds=-1)
