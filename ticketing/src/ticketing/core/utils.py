# -*- coding:utf-8 -*-
## todo:test

class IssuedAtBubblingSetter(object):
    """
    s = IssuedAtBubblingSetter(datetime.now())
    for t in tokens: #OrderedProductItemToken
       s.issued_token(t)
    s.start_bubbling()
    """
    def __init__(self, dt):
        self.tokens = set()
        self.items = set()
        self.orders = set() ##
        self.dt = dt

    def issued_token(self, token):
        self.tokens.add(token)

    def issued_item(self, item):
        self.items.add(item)
            
    def issued_order(self, order):
        self.orders.add(order)

    def _set_issued_at_iff_none(self, target):
        if target.issued_at is None:
            target.issued_at = self.dt

    def start_refresh_status_bubbling(self):
        assert self.dt is None
        for token in self.tokens:
            token.issued_at = None
            self.items.add(token.item)
        for item in self.items:
            item.issued_at = None
            self.orders.add(item.ordered_product.order)
        for order in self.orders:
            order.issued_at = None

    def start_bubbling(self):
        self.bubbling_tokens()
        self.bubbling_items()
        self.bubbling_orders()

    def bubbling_tokens(self):
        for token in self.tokens:
            self._set_issued_at_iff_none(token)
            item = token.item
            if not item in self.items:
                self.items.add(item)

    def bubbling_items(self):
        for item in self.items:
            if item.is_issued():
                self._set_issued_at_iff_none(item)
            order = item.ordered_product.order
            if not order in self.orders:
                self.orders.add(order)

    def bubbling_orders(self):
        for order in self.orders:
            if order.is_issued():
                self._set_issued_at_iff_none(order)

class PrintedAtBubblingSetter(object):
    """
    s = PrintedAtBubblingSetter(datetime.now())
    for t in tokens: #OrderedProductItemToken
       s.printed_token(t)
    s.start_bubbling()
    """
    def __init__(self, dt):
        self.tokens = set()
        self.items = set()
        self.orders = set() ##
        self.dt = dt

    def printed_token(self, token):
        self.tokens.add(token)

    def printed_item(self, item):
        self.items.add(item)
            
    def printed_order(self, order):
        self.orders.add(order)

    def _set_printed_at_iff_none(self, target):
        if target.printed_at is None:
            target.printed_at = self.dt

    def start_bubbling(self):
        self.bubbling_tokens()
        self.bubbling_items()
        self.bubbling_orders()

    def start_refresh_status_bubbling(self):
        assert self.dt is None
        for token in self.tokens:
            token.printed_at = None
            self.items.add(token.item)
        for item in self.items:
            item.printed_at = None
            self.orders.add(item.ordered_product.order)
        for order in self.orders:
            order.printed_at = None

    def bubbling_tokens(self):
        for token in self.tokens:
            self._set_printed_at_iff_none(token)
            item = token.item
            if not item in self.items:
                self.items.add(item)

    def bubbling_items(self):
        for item in self.items:
            if item.is_printed():
                self._set_printed_at_iff_none(item)
            order = item.ordered_product.order
            if not order in self.orders:
                self.orders.add(order)

    def bubbling_orders(self):
        for order in self.orders:
            if order.is_printed():
                if order.printed_at is None:
                    order.printed_at = self.dt
                order.issued = True

class IssuedPrintedAtSetter(object):
    def __init__(self, dt):
        self.for_issued = IssuedAtBubblingSetter(dt)
        self.for_printed = PrintedAtBubblingSetter(dt)

    def add_token(self, token):
        self.for_issued.issued_token(token)
        self.for_printed.printed_token(token)

    def add_item(self, item):
        self.for_issued.issued_item(item)
        self.for_printed.printed_item(item)

    def add_order(self, order):
        self.for_issued.issued_order(order)
        self.for_printed.printed_order(order)

    def start_bubbling(self):
        self.for_issued.start_bubbling()
        self.for_printed.start_bubbling()

    def start_refresh_status_bubbling(self):
        self.for_issued.start_refresh_status_bubbling()
        self.for_printed.start_refresh_status_bubbling()
