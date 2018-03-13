# encoding: utf-8

import logging
logger = logging.getLogger(__name__)

from zope.interface import implementer
from ..interfaces import IQRAESPlugin

import sqlahelper
from sqlalchemy.orm.session import object_session
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound, UnmappedInstanceError

from pyramid.httpexceptions import HTTPNotFound

from altair.app.ticketing.core.models import DeliveryMethodPlugin, TicketPrintHistory
from altair.app.ticketing.delivery_methods.interfaces import IDeliveryFormMaker
from altair.app.ticketing.delivery_methods.forms import DeliveryMethodForm
from altair.app.ticketing.orders.api import get_order_by_order_no
from altair.app.ticketing.orders.models import (Order,
                                                OrderedProduct,
                                                OrderedProductItem,
                                                OrderedProductItemToken)
from altair.app.ticketing.qr.builder import qr_aes

DBSession = sqlahelper.get_session()

def _get_db_session(history):
    try:
        return object_session(history)
    except UnmappedInstanceError:
        return DBSession

@implementer(IQRAESPlugin)
class QRAESPlugin(object):
    def __init__(self, key=None):
        self.builder = qr_aes(key)

    def make_data_for_qr(self, history):
        """
        :param history: TicketPrintHistory
        :return: dict()
        """
        return {}

    def get_matched_history_from_token(self, token):
        return TicketPrintHistory.filter(TicketPrintHistory.item_token_id == token.id).first()

    def get_matched_history_from_order(self, order):
        try:
            return TicketPrintHistory \
                .filter(TicketPrintHistory.seat_id == None) \
                .filter(TicketPrintHistory.item_token_id == None) \
                .filter(TicketPrintHistory.ordered_product_item_id == None) \
                .filter(TicketPrintHistory.order_id == order.id) \
                .one()
        except NoResultFound:
            return None

    def get_or_create_matched_history_from_token(self, order_no, token):
        history = self.get_matched_history_from_token(token)
        if history is None:
            logger.info("ticket print histry is not found. create it (orderno=%s,  token=%s)" % (order_no, token.id))
            history = TicketPrintHistory(
                seat_id=token.seat_id,
                item_token_id=token.id,
                ordered_product_item_id=token.ordered_product_item_id,
                order_id=token.item.ordered_product.order.id
            )
            DBSession.add(history)
            DBSession.flush()
        return history

    def get_matched_token_query_from_order(self, order):
        return OrderedProductItemToken.query \
            .filter(OrderedProductItemToken.ordered_product_item_id == OrderedProductItem.id) \
            .filter(OrderedProductItem.ordered_product_id == OrderedProduct.id) \
            .filter(OrderedProduct.order_id == order.id)

    def get_matched_token_query_from_order_no(self, order_no):
        return OrderedProductItemToken.query \
            .join(OrderedProductItemToken.item) \
            .join(OrderedProductItem.ordered_product) \
            .join(OrderedProduct.order) \
            .filter(Order.order_no == order_no)

    def get_matched_token_from_token_id(self,order_no, token_id, none_exception=HTTPNotFound):
        token = self.get_matched_token_query_from_order_no(order_no) \
            .filter(OrderedProductItemToken.id == token_id).first()
        if token is None:
            raise none_exception()
        return token

    def get_or_create_matched_history_from_order(self, order):
        history = self.get_matched_history_from_order(order)
        if history is None:
            logger.info("ticket print histry is not found. create it (order_no=%s)" % (order.order_no))
            history = TicketPrintHistory(
                seat_id=None,
                item_token_id=None,
                ordered_product_item_id=None,
                order_id=order.id
            )
            DBSession.add(history)
            DBSession.flush()
        return history

    def build_qr_by_history(self, history):
        data_for_qr = self.make_data_for_qr(history)
        ticket = data_for_qr.get('ticket', None)
        data = data_for_qr.get('data', None)
        ticket.qr = self.builder.make(data)
        ticket.sign = self.builder.make({'content':str(ticket.id)})
        return ticket

    def build_qr_by_ticket_id(self, ticket_id):
        try:
            history = TicketPrintHistory.filter_by(id=ticket_id).one()
            return self.build_qr_by_history(history)
        except (NoResultFound, MultipleResultsFound):
            return None

    def build_qr_by_token(self, order_no, token):
        history = self.get_or_create_matched_history_from_token(order_no, token)
        return self.build_qr_by_history(history)

    def build_qr_by_token_id(self, order_no, token_id, none_exception=HTTPNotFound):
        token = self.get_matched_token_from_token_id(order_no=order_no, token_id=token_id, none_exception=none_exception)
        return self.build_qr_by_token(order_no, token)

    def build_qr_by_order(self, order):
        history = self.get_or_create_matched_history_from_order(order)
        return self.build_qr_by_history(history)

    def build_qr_by_order_no(self, request, order_no, none_exception=HTTPNotFound):
        order = get_order_by_order_no(request, order_no)
        if order is None:
            raise none_exception
        return self.build_qr_by_order(order)

    def build_qr_by_sign(self, sign):
        if not sign:
            return None
        ticket_id = int(self.builder.extract(sign).get('content', None))
        if ticket_id:
            return self.build_qr_by_ticket_id(ticket_id)
        else:
            return None

    def output_to_template(self, ticket):
        return {'ticket': ticket}

class QRAESDeliveryMethodForm(DeliveryMethodForm):
    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        super(QRAESDeliveryMethodForm, self).__init__(formdata=formdata, obj=obj, prefix=prefix, **kwargs)
        self.delivery_plugin_id.choices = [(dmp.id, dmp.name) for dmp in DeliveryMethodPlugin.all()]

    def get_customized_fields(self):
        names = []
        for attr in dir(self):
            if attr.startswith('qr_aes_'):
                names.append(attr)
        return names

@implementer(IDeliveryFormMaker)
class QRAESDeliveryFormMaker(object):

    def make_form(self, formdata=None, obj=None, prefix='', **kwargs):
        return QRAESDeliveryMethodForm(formdata=formdata, obj=obj, prefix=prefix, **kwargs)