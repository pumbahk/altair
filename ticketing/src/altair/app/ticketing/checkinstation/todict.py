# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
from altair.viewhelpers.datetime_ import DefaultDateTimeFormatter, DateTimeHelper #xxx:
from .signer import Signer
from altair.app.ticketing.utils import todate

datetime_module = DateTimeHelper(DefaultDateTimeFormatter())
japanese_datetime = datetime_module.datetime

def verified_data_dict_from_secret(secret):
    """secret token"""
    signer = Signer(secret)
    return {"secret": signer.sign()}


from altair.app.ticketing.payments.plugins import QR_DELIVERY_PLUGIN_ID
class TokenStatus:
    valid = "valid"
    printed = "printed"
    canceled = "canceled"
    before_start = "before_start"
    after_end = "after_end"
    over_print_limit = "over_print_limit"
    not_supported = "not_supported"
    unknown = "unknown"

class TokenStatusDictBuilder(object):
    def __init__(self, order, history=None, today=None, refreshmode=None):
        self.order = order
        self.history = history

        self.today = today
        self.refreshmode = refreshmode

        self.token = self.history.item_token if history else None
        self.performance = self.order.performance


    def build(self):
        D = {"status": TokenStatus.valid}
        D.update(self.printed_status_dict())
        D.update(self.canceled_status_dict())
        D.update(self.printable_date_status_dict())
        D.update(self.over_print_limit_dict())
        D.update(self.supported_status_dict())
        return D

    def printed_status_dict(self):
        # 再発券許可モードは無条件で未発券
        if self.refreshmode:
            return {"printed_at": None}

        if self._is_unprinted_yet(self.order, self.token):
            return {"printed_at": None}
        else:
            return {"printed_at":japanese_datetime((self.token or self.order).printed_at), "status": TokenStatus.printed}

    def canceled_status_dict(self):
        order=self.order
        if self._is_canceled(order):
            logger.info("*status order is already canceled (order.id=%s, order.order_no= %s)",  order.id,  order.order_no)
            return {"canceled_at":japanese_datetime(self.order.canceled_at), "status": TokenStatus.canceled}
        else:
            return {"canceled_at": None}

    def supported_status_dict(self, delivery_plugin_id=QR_DELIVERY_PLUGIN_ID):
        order=self.order
        if self._is_supported_order(order):
            return {}
        else:
            logger.info("*status order's PDMP is not dupported (order.id=%s, order.order_no= %s,  pdmp.id=%s)", order.id,  order.order_no,  self.order.payment_delivery_method_pair.id)
            return {"status": TokenStatus.not_supported}

    def printable_date_status_dict(self):
        if self.today is None:
            return {}
        elif not self._is_printable_date_before_start(self.order, self.today):
            order = self.order
            logger.info("*status order's performance is before start date. (order.id=%s, order.order_no=%s, performance.id=%s)", order.id, order.order_no, self.performance.id)
            return {}
            # return {"status": TokenStatus.before_start}
        elif not self._is_printable_date_after_end(self.order, self.today):
            order = self.order
            logger.info("*status order's performance is already end. (order.id=%s, order.order_no=%s, performance.id=%s)", order.id, order.order_no, self.performance.id)
            return {"status": TokenStatus.after_end}
        else:
            return {}

    def over_print_limit_dict(self):
        print_num = 0
        for item in self.order.items:
            print_num += item.seat_quantity

        if print_num > 10:
            order = self.order
            logger.info("*status print limit overed  (order.id=%s, order.order_no=%s)", order.id, order.order_no)
            return {"status": TokenStatus.over_print_limit}
        return {}

    def _is_canceled(self, order):
        return order is None or order.is_canceled()

    def _is_unprinted_yet(self, order, token):
        return ((token is None or not token.is_printed()) 
                and (order and order.printed_at is None))

    def _is_printable_date_before_start(self, order, today):
        performance = order.performance
        pdmp = order.payment_delivery_method_pair
        if pdmp and pdmp.issuing_start_at:
            return todate(today) >= todate(min(pdmp.issuing_start_at, (performance.start_on or performance.open_on)))
        else:
            logger.info("check printable date: issuing start at is not set. using performance.open_on (order id=%s)", order.id)
            return todate(today) >= todate(performance.open_on or performance.start_on)

    def _is_printable_date_after_end(self, order, today):
        performance = order.performance
        if performance.end_on:
            return today <= performance.end_on
        else:
            return todate(today) <= todate(performance.start_on)


    def _is_supported_order(self, order):
        delivery_method = order.payment_delivery_method_pair.delivery_method
        return delivery_method.delivery_plugin_id == QR_DELIVERY_PLUGIN_ID


def additional_data_dict_from_order(order):
    performance = order.performance
    shipping_address = order.shipping_address
    performance_name = performance.name
    note = order.note
    return {"additional":
            {
                "user": shipping_address.full_name_kana if shipping_address else u"",
                "order": {
                    "order_no": order.order_no, 
                    "id": unicode(order.id), 
                    "note": note,
                }, 
                "performance": {
                    "id": unicode(performance.id), 
                    "name": performance_name, 
                    "date":japanese_datetime(performance.start_on), 
                }, 
                "event": {
                    "id": unicode(performance.event_id)
                }
            }}

def ticket_data_collection_dict_from_tokens(tokens, mask_predicate=None, refreshmode=None):
    collection = []
    for token in tokens:
        seat = token.seat
        D = {
            "refreshed_at": unicode(token.refreshed_at) if token.refreshed_at else None, 
            "printed_at": unicode(token.printed_at) if token.is_printed() and not refreshmode else None,
            "locked_at": "", 
            "ordered_product_item_token_id": unicode(token.id), 
            "seat": {
                "id": unicode(seat.id) if seat else None,
                "name": seat.name if seat else u"自由席",
            }, 
            "product": {
                "name": token.item.ordered_product.product.name
            }}
        if mask_predicate and mask_predicate.is_masked(token.id):
            D["printed_at"] = u"(他端末で発券中)"
            D["locked_at"] = japanese_datetime(mask_predicate.get_masked_expired_at_string(token.id))
        collection.append(D)
    return {"collection": collection}

def ticket_data_dict_from_history(history):
    """variant of printqr.todict.data_dict_from_order_and_history"""
    product_name = history.ordered_product_item.ordered_product.product.name if history.ordered_product_item else None
    token = history.item_token
    seat = history.seat
    codeno = history.id
    return {
        "codeno": unicode(codeno), 
        "refreshed_at": unicode(token.refreshed_at) if token and token.refreshed_at else None,
        "printed_at": unicode(token.printed_at) if token and token.is_printed() else None,
        "ordered_product_item_token_id": token and unicode(token.id),
        "product": {
            "name":  product_name
        }, 
        "seat": {
            "id": unicode(seat.id) if seat else None,
            "name": seat.name if seat else u"自由席",
        }
    }


def dict_from_performance(performance):
    return {"id": unicode(performance.id), 
            "name": performance.name, 
            "event_id": performance.event_id, 
            "start_on": performance.start_on, 
            "end_on": performance.end_on
        }
