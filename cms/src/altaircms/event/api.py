# coding: utf-8
import logging
import isodate
from sqlalchemy.orm.exc import NoResultFound

from altaircms.event.models import Event
from altaircms.models import DBSession, Performance, Sale, Ticket
from altaircms.auth.models import APIKey
from altaircms.seeds.prefecture import PREFECTURE_CHOICES

class EventRepositry(object):
    def parse_and_save_event(self, parsed):
        return parse_and_save_event(parsed)

def parse_datetime(dtstr):
    if dtstr is None:
        return None
    try:
        return isodate.parse_datetime(dtstr)
    except ValueError:
        raise "Invalid ISO8601 datetime: %s" % dtstr

class Scanner(object):
    def __init__(self, session):
        self.session = session
        self.current_event = None
        self.current_performance = None
        self.current_sale = None
        self.current_ticket = None
        self.events = []
        self.prefectures = dict([(v, k) for k, v in PREFECTURE_CHOICES])
        self.after_parsed_actions = []

    def scan_ticket_record(self, ticket_record):
        ticket = Ticket.query.filter_by(backend_id=ticket_record['id']).first() or Ticket()

        deleted = ticket_record.get('deleted', False)
        if deleted:
            Ticket.query.filter_by(backend_id=ticket_record['id']).delete()
        else:
            try:
                ticket.sale = Sale.query.filter_by(backend_id=ticket_record['sale_id']).first()
                ticket.backend_id = ticket_record['id']
                ticket.name = ticket_record['name']
                ticket.seattype = ticket_record['seat_type']
                ticket.price = ticket_record['price']
            except KeyError as e:
                raise "missing property '%s' in the ticket record" % e.message
            self.session.add(ticket)

    def scan_sales_segment_record(self, sales_segment_record):
        sale = Sale.query.filter_by(backend_id=sales_segment_record['id']).first() or Sale()

        deleted = sales_segment_record.get('deleted', False)
        if deleted:
            Sale.query.filter_by(backend_id=sales_segment_record['id']).delete()
        else:
            try:
                sale.event = self.current_event
                sale.backend_id = sales_segment_record["id"]
                sale.name = sales_segment_record["name"]
                sale.kind = sales_segment_record["kind"]
                sale.start_on = parse_datetime(sales_segment_record['start_on'])
                sale.end_on = parse_datetime(sales_segment_record['end_on'])
            except KeyError as e:
                raise Exception("missing property '%s' in the sales record" % e.message)
            self.session.add(sale)

    def scan_performance_record(self, performance_record):
        performance = Performance.query.filter_by(backend_id=performance_record['id']).first() or Performance()

        deleted = performance_record.get('deleted', False)
        if deleted:
            Performance.query.filter_by(backend_id=performance_record['id']).delete()
        else:
            try:
                performance.event = self.current_event
                performance.backend_id = performance_record['id']
                performance.title = performance_record['name']
                performance.venue = performance_record['venue']
                performance.prefecture = self.prefectures.get(performance_record['prefecture'])
                performance.open_on = parse_datetime(performance_record['open_on'])
                performance.start_on = parse_datetime(performance_record['start_on'])
                performance.end_on = parse_datetime(performance_record.get('end_on'))
                def bound_performance_to_tickets():
                    """ チケットが生成されてから、performanceとticketを結びつける。"""
                    ## 更新により通知されるticket.backend`idsが減ったとき、増えたときのテストしていない。
                    ticket_id_list = performance_record.get("tickets", [])
                    performance.tickets = list(Ticket.query.filter(Ticket.backend_id.in_(ticket_id_list)))
                self.after_parsed_actions.append(bound_performance_to_tickets)

            except KeyError as e:
                raise Exception("missing property '%s' in the event record" % e.message)
            self.session.add(performance)

    def scan_event_record(self, event_record):
        event = Event.query.filter_by(backend_id=event_record['id']).first() or Event()

        deleted = event_record.get('deleted', False)
        if not deleted:
            try:
                event.backend_id = event_record['id']
                event.title = event_record['title']
                event.subtitle = event_record.get('subtitle', '')
                event.event_open = parse_datetime(event_record['start_on'])
                event.event_close = parse_datetime(event_record['end_on'])
                event.deal_open = parse_datetime(event_record.get('deal_open'))
                event.deal_close = parse_datetime(event_record.get('deal_close'))
            except KeyError as e:
                raise Exception("missing property '%s' in the event record" % e.message)

        self.current_event = event

        performance_records = event_record.get('performances')
        if performance_records is None:
            raise ValueError("'performances' property not present in the event record")
        for performance_record in performance_records:
            self.scan_performance_record(performance_record)

        sales_segment_records = event_record.get('sales')
        if sales_segment_records is None:
            raise ValueError("'sales' property not present in the event record")
        for sales_segment_record in sales_segment_records:
            self.scan_sales_segment_record(sales_segment_record)

        ticket_records = event_record.get('tickets')
        if ticket_records is None:
            raise ValueError("'tickets' property not present in the event record")
        for ticket_record in ticket_records:
            self.scan_ticket_record(ticket_record)

        if deleted:
            Event.query.filter_by(backend_id=event_record['id']).delete()
        else:
            self.session.add(event)
            self.events.append(event)

    def scan_toplevel(self, parsed):
        event_records = parsed.get('events')
        if event_records is None:
            raise ValueError("'events' property not present in the toplevel of the payload")
        for event_record in event_records:
            self.scan_event_record(event_record)

    def __call__(self, parsed):
        self.scan_toplevel(parsed)
        for action in self.after_parsed_actions:
            action()
        return self.events

def parse_and_save_event(parsed):
    # import pprint
    # pprint.pprint(parsed)
    return Scanner(DBSession)(parsed)

def validate_apikey(apikey):
    try:
        APIKey.query.filter_by(apikey=apikey).one()
    except NoResultFound:
        return False
    return True
