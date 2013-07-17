# -*- coding:utf-8 -*-

class OrderCanceled(object):
    def __init__(self, request, order):
        self.request = request
        self.order = order

def notify_order_canceled(request, order):
    reg = request.registry
    event = OrderCanceled(request, order)
    reg.notify(event)
