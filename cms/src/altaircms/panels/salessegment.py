# -*- coding:utf-8 -*-
# see. __init__.py
from altaircms.lib.itertools import find_or_first
from .viewhelpers import TicketGrid

def salessegment_describe_panel(context, request, salessegment):
    return dict(salessegment=salessegment)

def salessegment_ticket_tabs_panel(context, request, salessegment, id_key="ticket_id"):
    tickets = salessegment.tickets
    ticket_id = unicode(request.GET.get(id_key))
    current_ticket = find_or_first(tickets, lambda s : unicode(s.id) == ticket_id)
    grid = TicketGrid.create(tickets)
    return dict(current_ticket=current_ticket, 
                salessegment=salessegment, 
                grid=grid, tickets=tickets, 
                page_title=u"商品")
