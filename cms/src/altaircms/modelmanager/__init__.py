from .faker import ModelFaker
from pyramid.decorator import reify

class SalesTermSummalize(object):
    def __init__(self, request):
        self.request = request

    def summalize_event(self, event, virtual=False):
        return EventSalesTerm(event, virtual=virtual)

    def summalize_salessegment_group(self, salessegment_group, virtual=False):
        return SalesSegmentGroupSalesTerm(salessegment_group, virtual=virtual)

    def summalize_salessegment(self, salessegment, virtual=False):
        return SalesSegmentSalesTerm(salessegment, virtual=virtual)


class SalesTermBase(object):
    def __init__(self, o, virtual=False):
        self.virtual = virtual
        if virtual:
            self.o = ModelFaker(o)
        else:
            self.o = o

class EventSalesTerm(SalesTermBase):
    @reify
    def children(self):
        return [SalesSegmentGroupSalesTerm(s, virtual=self.virtual) for s in self.o.salessegment_groups]

    def term(self):
        children = self.children
        if not children:
            return self.o.deal_open, self.o.deal_close
        first_start_date, final_end_date = children[0].term()
        for c in children:
            start_date, end_date = c.term()
            if first_start_date > start_date:
                first_start_date = start_date
            if final_end_date < end_date:
                final_end_date = end_date
        self.o.deal_open = first_start_date
        self.o.deal_close = final_end_date
        return first_start_date, final_end_date

    def bubble(self, start_on, end_on):
        o = self.o
        if start_on < o.deal_open:
            o.deal_open = start_on
        if end_on > o.deal_close:
            o.deal_close = end_on
        return o.deal_open, o.deal_close

class SalesSegmentGroupSalesTerm(SalesTermBase):
    @reify
    def children(self):
        return [SalesSegmentSalesTerm(s, virtual=self.virtual) for s in self.o.salessegments]

    def term(self):
        children = self.children
        if not children:
            return self.o.start_on, self.o.end_on
        first_start_date, final_end_date = children[0].term()
        for c in children:
            start_date, end_date = c.term()
            if first_start_date > start_date:
                first_start_date = start_date
            if final_end_date < end_date:
                final_end_date = end_date
        self.o.start_on = first_start_date
        self.o.end_on = final_end_date
        return first_start_date, final_end_date

    def bubble(self, start_on, end_on):
        o = self.o
        if start_on < o.start_on:
            o.start_on = start_on
        if end_on > o.end_on:
            o.end_on = end_on
        parent = EventSalesTerm(o.event)
        return parent.bubble(o.start_on, o.end_on)

class SalesSegmentSalesTerm(SalesTermBase):
    children = []
    def term(self):
        return self.o.start_on, self.o.end_on

    def bubble(self, start_on=None, end_on=None):
        parent = SalesSegmentGroupSalesTerm(self.o.group)
        return parent.bubble(self.o.start_on, self.o.end_on)
