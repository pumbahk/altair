# coding: utf-8
import json

import isodate
import transaction
from sqlalchemy.orm.exc import NoResultFound
import sqlahelper

from altaircms.event.models import Event
from altaircms.models import DBSession, Performance, Sale, Ticket
from altaircms.auth.models import APIKey

class EventRepositry(object):
    def parse_and_save_event(self, parsed):
        return parse_and_save_event(parsed)

def event_from_dict(d):
    event_obj = Event()
    event_obj.backend_event_id = d['id']
    event_obj.name = d['name']
    event_obj.event_on = isodate.parse_datetime(d['start_on'])
    event_obj.event_close = isodate.parse_datetime(d['end_on'])
    return event_obj

def performance_from_dict(d):
    performance_obj = Performance()
    performance_obj.backend_performance_id = d['id']
    performance_obj.title = d['name']
    performance_obj.venue = d['venue']
    performance_obj.open_on = isodate.parse_datetime(d['open_on'])
    performance_obj.start_on = isodate.parse_datetime(d['start_on'])
    performance_obj.close_on = isodate.parse_datetime(d['close_on']) if 'close_on' in d else None
    return performance_obj

def sale_from_dict(d):
    sale_obj = Sale()
    sale_obj.name = d['name']
    sale_obj.start_on = isodate.parse_datetime(d['start_on'])
    sale_obj.end_on = isodate.parse_datetime(d['end_on'])

    return sale_obj

def ticket_from_dict(d):

    ticket_obj = Ticket()
    ticket_obj.name = d['name']
    ticket_obj.price = d['price']
    ticket_obj.seat_type = d['seat_type']

    return ticket_obj
    
def parse_and_save_event(parsed):

    events = []
    # @FIXME: 再帰にした方がいいかも
    for event in parsed['events']:
        if 'deleted' in event and event['deleted'] is True:
            event_obj = DBSession.query(Event).filter_by(id=event['id']).one()
            DBSession.delete(event_obj)
        else:
            event_obj = event_from_dict(event)
            DBSession.add(event_obj)
            events.append(event_obj)

        for performance in event.get('performances', []):
            if 'deleted' in performance and performance['deleted'] is True:
                performance_obj = DBSession.query(Performance).filter_by(id=performance['id']).one()
                DBSession.delete(performance_obj)
            else:
                performance_obj = performance_from_dict(performance)
                performance_obj.event = event_obj

            for sale in performance.get('sales', []):
                if 'deleted' in sale and sale['deleted'] is True:
                    sale_obj = DBSession.query(Sale).filter_by(id=sale['id']).one()
                    DBSession.delete(sale_obj)
                else:
                    sale_obj = sale_from_dict(sale)
                    sale_obj.performance = performance_obj

                for ticket in sale.get('tickets', []):
                    if 'deleted' in ticket and ticket['deleted'] is True:
                        ticket_obj = DBSession.query(Ticket).filter_by(id=ticket['id']).one()
                        DBSession.delete(ticket_obj)
                    else:
                        ticket_obj = ticket_from_dict(ticket)
                        ticket_obj.sale = sale_obj

    return events


def validate_apikey(apikey):
    try:
        APIKey.query.filter_by(apikey=apikey).one()
    except NoResultFound:
        return False
    return True
