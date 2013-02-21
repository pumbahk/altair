from .faker import ModelFaker
from pyramid.decorator import reify


## sales term

class SalesTermSummalize(object):
    def __init__(self, request):
        self.request = request

    def summalize_event(self, event, virtual=False):
        return EventSalesTerm(event, virtual=virtual)

    def summalize_salessegment_group(self, salessegment_group, virtual=False):
        return SalesSegmentGroupSalesTerm(salessegment_group, virtual=virtual)

    def summalize_salessegment(self, salessegment, virtual=False):
        return SalesSegmentSalesTerm(salessegment, virtual=virtual)

class BubblingBase(object):
    def __init__(self, o, virtual=False):
        self.virtual = virtual
        if virtual:
            self.o = ModelFaker(o)
        else:
            self.o = o

class EventSalesTerm(BubblingBase):
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

class SalesSegmentGroupSalesTerm(BubblingBase):
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

class SalesSegmentSalesTerm(BubblingBase):
    children = []
    def term(self):
        return self.o.start_on, self.o.end_on

    def bubble(self, start_on=None, end_on=None):
        parent = SalesSegmentGroupSalesTerm(self.o.group)
        return parent.bubble(self.o.start_on, self.o.end_on)

## updated_at

class UpdatedAtSummalize(object):
    def __init__(self, request):
        self.request = request

    def summalize_page(self, obj, virtual=False):
        return PageUpdatedAt(obj, virtual=virtual)

    def summalize_performance(self, obj, virtual=False):
        return PerformanceUpdatedAt(obj, virtual=virtual)

    def summalize_salessegment_group(self, obj, virtual=False):
        return SalesSegmentGroupUpdatedAt(obj, virtual=virtual)

    def summalize_salessegment(self, obj, virtual=False):
        return SalesSegmentUpdatedAt(obj, virtual=virtual)

    def summalize_ticket(self, obj, virtual=False):
        return TicketUpdatedAt(obj, virtual=virtual)


class EventUpdatedAt(BubblingBase):
    def bubble(self, updated_at):
        self.o.updated_at = updated_at
    
class PageSetUpdatedAt(BubblingBase):
    def bubble(self, updated_at):
        self.o.updated_at = updated_at
        parent = EventUpdatedAt(self.o.event)
        parent.bubble(updated_at)
        
class PageUpdatedAt(BubblingBase):
    def bubble(self, updated_at):
        self.o.updated_at = updated_at
        parent = PageSetUpdatedAt(self.o.pageset)
        return parent.bubble(self.o.updated_at)
        
class PerformanceUpdatedAt(BubblingBase):
    def bubble(self, updated_at):
        self.o.updated_at = updated_at
        parent = EventUpdatedAt(self.o.event)
        return parent.bubble(self.o.updated_at)

class SalesSegmentGroupUpdatedAt(BubblingBase):
    def bubble(self, updated_at):
        self.o.updated_at = updated_at
        parent = EventUpdatedAt(self.o.event)
        return parent.bubble(self.o.updated_at)
    
class SalesSegmentUpdatedAt(BubblingBase):
    def bubble(self, updated_at):
        self.o.updated_at = updated_at
        parent = SalesSegmentGroupUpdatedAt(self.o.group)
        return parent.bubble(self.o.updated_at)
    
class TicketUpdatedAt(BubblingBase):
    def bubble(self, updated_at):
        self.o.updated_at = updated_at
        parent = SalesSegmentGroupUpdatedAt(self.o.salessegment)
        return parent.bubble(self.o.updated_at)
