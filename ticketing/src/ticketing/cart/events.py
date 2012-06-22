class OrderCompleted(object):
    def __init__(self, request, order):
        self.request = request
        self.order = order

def notify_order_completed(request, order):
    reg = request.registry
    event = OrderCompleted(request, order)
    reg.notify(event)
