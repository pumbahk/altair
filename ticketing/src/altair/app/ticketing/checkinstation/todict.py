# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
from altair.viewhelpers.datetime_ import DefaultDateTimeFormatter, DateTimeHelper #xxx:
from .signer import Signer

datetime_module = DateTimeHelper(DefaultDateTimeFormatter())
japanese_datetime = datetime_module.datetime

def verified_data_dict_from_secret(secret):
    """secret token"""
    signer = Signer(secret)
    return {"secret": signer.sign()}


##token status = {valid, canceled, printed, unknown}
class TokenStatusDictBuilder(object):
    def __init__(self, order, history=None):
        self.order = order
        self.history = history
        self.token = history.item_token if history else None

    def build(self):
        D = {"status": "valid"}
        D.update(self.printed_status_dict())
        D.update(self.canceled_status_dict())
        return D

    def printed_status_dict(self):
        if self.token is None or not self.token.is_printed():
            return {"printed_at": None}
        else:
            return {"printed_at":japanese_datetime(self.token.printed_at), "status": "printed"}

    def canceled_status_dict(self):
        if self.order is None or not self.order.is_canceled():
            return {"canceled_at": None}
        else:
            return {"canceled_at":japanese_datetime(self.order.canceled_at), "status": "canceled"}


def data_dict_from_order_and_history(order, history):
    """variant of printqr.todict.data_dict_from_order_and_history"""
    performance = order.performance
    shipping_address = order.shipping_address
    product_name = history.ordered_product_item.ordered_product.product.name
    token = history.item_token
    seat = history.seat
    performance_name = u"%s (%s)" % (performance.name, performance.venue.name)
    note = order.note

    codeno = history.id
    return {
        "codeno": codeno, 
        "refreshed_at": str(token.refreshed_at) if token.refreshed_at else None, 
        "printed_at": str(token.printed_at) if token.printed_at else None, 
        "ordered_product_item_token_id": token.id, 
        "product": {
            "name":  product_name
        }, 
        "seat": {
            "id": seat.id if seat else None,
            "name": seat.name if seat else u"自由席",
        }, 
        "additional": {
            "user": shipping_address.full_name_kana if shipping_address else u"",
            "order": {
                "order_no": order.order_no, 
                "id": order.id, 
                "note": note,
            }, 
            "performance": {
                "id": performance.id, 
                "name": performance_name, 
                "date":japanese_datetime(performance.start_on), 
            }, 
            "event": {
                "id": performance.event_id
            }, 
            "ordered_product_item":{
                "id": history.ordered_product_item.id,
            }, 
        }
    }


def dict_from_performance(performance):
    return {"id": performance.id, 
            "name": performance.name, 
            "event_id": performance.event_id, 
            "start_on": performance.start_on, 
            "end_on": performance.end_on
        }
