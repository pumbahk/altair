# coding: utf-8
import json

import isodate
import transaction
from sqlalchemy.orm.exc import NoResultFound

from altaircms.models import Event, DBSession, Performance, Sale, Ticket
from altaircms.auth.models import APIKey

def parse_and_save_event(jsonstring):
    parsed = json.loads(jsonstring)

    try:
        for event in parsed['events']:
            event_obj = Event()
            event_obj.backend_event_id = event['id']
            event_obj.name = event['name']
            event_obj.event_on = isodate.parse_datetime(event['start_on'])
            event_obj.event_close = isodate.parse_datetime(event['end_on'])
            DBSession.add(event_obj)
            event_obj = DBSession.merge(event_obj)

            if 'performances' in event:
                for performance in event['performances']:
                    performance_obj = Performance()
                    performance_obj.event_id = event_obj.id
                    performance_obj.backend_performance_id = performance['id']
                    performance_obj.title = performance['name']
                    performance_obj.place = performance['venue']
                    performance_obj.open_on = isodate.parse_datetime(performance['open_on'])
                    performance_obj.start_on = isodate.parse_datetime(performance['start_on'])
                    # performance_obj.end_on = isodate.parse_datetime(performance['end_on'])  # TODO: end_onの必須有無確認
                    performance_obj.end_on = isodate.parse_datetime(performance['end_on']) if 'end_on' in performance else None
                    DBSession.add(performance_obj)
                    performance_obj = DBSession.merge(performance_obj)

                    if 'sales' in performance:
                        for sale in performance['sales']:
                            sale_obj = Sale()
                            sale_obj.performance_id = performance_obj.id
                            sale_obj.name = sale['name']
                            sale_obj.start_on = isodate.parse_datetime(sale['start_on'])
                            sale_obj.end_on = isodate.parse_datetime(sale['end_on'])
                            DBSession.add(sale_obj)
                            sale_obj = DBSession.merge(sale_obj)

                            if 'tickets' in sale:
                                for ticket in sale['tickets']:
                                    ticket_obj = Ticket()
                                    ticket_obj.sale_id = sale_obj.id
                                    ticket_obj.name = ticket['name']
                                    ticket_obj.price = ticket['price']
                                    ticket_obj.seat_type = ticket['seat_type']
                                    DBSession.add(ticket_obj)
                                    ticket_obj = DBSession.merge(ticket_obj)
    except:
        raise

    transaction.commit()

    return True

def validate_apikey(apikey):
    try:
        DBSession.query(APIKey).filter_by(apikey=apikey).one()
    except NoResultFound:
        return False
    return True
