# -*- coding:utf-8 -*-
from .faker import ModelFaker
from pyramid.decorator import reify
from altaircms.models import Performance, SalesSegment, SalesSegmentGroup
## sales term
class EventTermSummalize(object):
    def __init__(self, request):
        self.request = request

    def summalize(self, obj, virtual=False):
        return getattr(self, "summalize_%s" % obj.__class__.__name__)(obj, virtual=virtual)

    def summalize_Event(self, event, virtual=False):
        return EventEventTerm(event, virtual=virtual)

    def summalize_Performance(self, event, virtual=False):
        return PerformanceEventTerm(event, virtual=virtual)

class SalesTermSummalize(object):
    def __init__(self, request):
        self.request = request

    def summalize(self, obj, virtual=False):
        return getattr(self, "summalize_%s" % obj.__class__.__name__)(obj, virtual=virtual)

    def summalize_Event(self, event, virtual=False):
        return EventSalesTerm(event, virtual=virtual)

    def summalize_SalesSegmentGroup(self, salessegment_group, virtual=False):
        return SalesSegmentGroupSalesTerm(salessegment_group, virtual=virtual)

    def summalize_SalesSegment(self, salessegment, virtual=False):
        return SalesSegmentSalesTerm(salessegment, virtual=virtual)

class BubblingBase(object):
    def __init__(self, o, virtual=False):
        self.virtual = virtual
        if virtual:
            self.o = ModelFaker(o)
        else:
            self.o = o

class EventEventTerm(BubblingBase):
    @reify
    def children(self):
#        return [PerformanceEventTerm(p, virtual=self.virtual) for p in self.o.performances]
        return [PerformanceEventTerm(p, virtual=self.virtual) for p in Performance.query.filter(Performance.event_id==self.o.id)]

    def term(self):
        children = self.children
        if not children:
            return self.o.deal_open, self.o.deal_close
        first_start_date, final_end_date = children[0].term()
        for c in children[1:]:
            start_date, end_date = c.term()
            if first_start_date > start_date:
                first_start_date = start_date
            if final_end_date < end_date:
                final_end_date = end_date
        self.o.event_open = first_start_date
        self.o.event_close = final_end_date
        return first_start_date, final_end_date

    def bubble(self): #手抜き。全部調べる。
        self.term()
        return self.o.deal_open, self.o.deal_close
    
class PerformanceEventTerm(BubblingBase):
    children = []
    def term(self):
        return self.o.start_on, self.o.end_on

    def bubble(self, start_on=None, end_on=None):
        parent = EventEventTerm(self.o.event)
        return parent.bubble()

class EventSalesTerm(BubblingBase):
    @reify
    def children(self):
        return [SalesSegmentGroupSalesTerm(s, virtual=self.virtual) for s in SalesSegmentGroup.query.filter(SalesSegmentGroup.event_id==self.o.id)]
        # return [SalesSegmentGroupSalesTerm(s, virtual=self.virtual) for s in self.o.salessegment_groups]

    def term(self):
        children = self.children
        if not children:
            return self.o.deal_open, self.o.deal_close
        first_start_date, final_end_date = children[0].term()
        for c in children[1:]:
            start_date, end_date = c.term()
            if first_start_date > start_date:
                first_start_date = start_date
            if final_end_date < end_date:
                final_end_date = end_date
        self.o.deal_open = first_start_date
        self.o.deal_close = final_end_date
        return first_start_date, final_end_date

    def bubble(self): #手抜き。全部調べる。
        self.term()
        return self.o.deal_open, self.o.deal_close

class SalesSegmentGroupSalesTerm(BubblingBase):
    @reify
    def children(self):
        return [SalesSegmentSalesTerm(s, virtual=self.virtual) for s in SalesSegment.query.filter(SalesSegment.group_id==self.o.id)]
        # return [SalesSegmentSalesTerm(s, virtual=self.virtual) for s in self.o.salessegments]

    def term(self):
        children = self.children
        if not children:
            return self.o.start_on, self.o.end_on
        first_start_date, final_end_date = children[0].term()
        for c in children[1:]:
            start_date, end_date = c.term()
            if first_start_date > start_date:
                first_start_date = start_date
            if final_end_date < end_date:
                final_end_date = end_date
        self.o.start_on = first_start_date
        self.o.end_on = final_end_date
        return first_start_date, final_end_date

    def bubble(self):
        parent = EventSalesTerm(self.o.event)
        return parent.bubble()

class SalesSegmentSalesTerm(BubblingBase):
    children = []
    def term(self):
        return self.o.start_on, self.o.end_on

    def bubble(self, start_on=None, end_on=None):
        parent = SalesSegmentGroupSalesTerm(self.o.group)
        return parent.bubble()

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
