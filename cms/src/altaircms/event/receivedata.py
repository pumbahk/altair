# coding: utf-8
import logging
logger = logging.getLogger(__name__)
import isodate
from altaircms.event.models import Event
from altaircms.auth.models import Organization
from altaircms.models import Performance, SalesSegment, Ticket, SalesSegmentGroup
from altaircms.seeds.prefecture import PREFECTURE_CHOICES
from . import subscribers

def parse_datetime(dtstr):
    if dtstr is None:
        return None
    try:
        return isodate.parse_datetime(dtstr)
    except ValueError:
        raise "Invalid ISO8601 datetime: %s" % dtstr

ORGANIZATION_SOURCE = "oauth" #todo backend api include this

class ModelFetcher(object):
    def __init__(self, model):
        self.model = model
        self.cache = {}
        self.fetch_keys = set()
        self.data = {}

    def add(self, k, datum, env=None):
        self.data[k] = (datum, env)
        self.fetch_keys.add(k)

    def keys(self):
        return list(self.fetch_keys)

    def cached_keys(self):
        return (m.id for m in self.cache.itervalues())

    def merge(self, params):
        self.cache.update(params)

    @property
    def data_iter(self):
        return self.data.iteritems()


PREFECTURES = dict([(v, k) for k, v in PREFECTURE_CHOICES])

def strict_get(parsed, k, msg=None):
    v = parsed.get(k)
    if v is None:
        msg = msg or "'%s' property not present in the params"
        raise ValueError(msg)
    return v

class Scanner(object):
    def __init__(self, session, request):
        self.session = session
        self.request = request

        self.event_fetcher = ModelFetcher(Event)
        self.performance_fetcher = ModelFetcher(Performance)
        self.salessegment_fetcher = ModelFetcher(SalesSegment)
        self.ticket_fetcher = ModelFetcher(Ticket)

        self.after_parsed_actions = []

    def scan_toplevel(self, parsed):
        ## organization
        organization = strict_get(parsed, "organization")

        ## event
        events = parsed.get("events", [])
        for event in events:
            nenv = {"event": event, "organization": organization}
            self.scan_event_record(event, nenv)

    def scan_event_record(self, record, env):
        _id = strict_get(record, "id")
        self.event_fetcher.add(_id, record, env)
        for performance in record.get("performances", []):
            nenv = {"event": record}
            nenv.update(env)
            self.scan_performance_record(performance, nenv)

    def scan_performance_record(self, record, env):
        _id = strict_get(record, "id")
        self.performance_fetcher.add(_id, record, env)
        for sale in record.get("sales", []):
            nenv = {"performance": record}
            nenv.update(env)
            self.scan_sale_record(sale, nenv)

    # rename salessegment?
    def scan_sale_record(self, record, env):
        _id = strict_get(record, "id")
        self.salessegment_fetcher.add(_id, record, env)
        for ticket in record.get("tickets", []):
            nenv = {"sale": record}
            nenv.update(env)
            self.scan_ticket_record(ticket, nenv)

    # rename product?
    def scan_ticket_record(self, record, env):
        _id = strict_get(record, "id")
        self.ticket_fetcher.add(_id, record, env)


    ## fetch
    def fetch_organization(self, parsed):
        ## organization
        record = strict_get(parsed, "organization")
        organization = Organization.get_or_create(record["id"], ORGANIZATION_SOURCE)
        organization.short_name = record.get("short_name")
        self.session.add(organization)
        self.session.flush()
        return organization

    def fetch_events(self, organization):
        fetcher = self.event_fetcher
        ks = fetcher.keys()
        if ks:
            models = Event.query.filter(Event.organization_id==organization.id, Event.backend_id.in_(ks)).all()
            fetcher.merge({m.backend_id: m for m in models})

        r = []
        for backend_id, (record, env) in self.event_fetcher.data_iter:
            event = fetcher.cache.get(backend_id)
            if event is None:
                event = fetcher.cache[backend_id] = Event()
            try:
                if record.get("deleted"):
                    self.session.delete(event) #need lazy?
                    continue
                r.append(event)
                event.backend_id = backend_id
                event.title = record['title']
                event.subtitle = record.get('subtitle', '')
                event.event_open = parse_datetime(record['start_on'])
                event.event_close = parse_datetime(record['end_on'])
                event.deal_open = parse_datetime(record.get('deal_open'))
                event.deal_close = parse_datetime(record.get('deal_close'))
                event.organization_id = organization.id
                def notify_event_update():
                    subscribers.notify_event_update(self.request, event)
                self.after_parsed_actions.append(notify_event_update)
            except KeyError as e:
                raise Exception("missing property '%s' in the event record" % e.message)
        return r
            
    def fetch_performances(self, organization):
        fetcher = self.performance_fetcher
        ks = fetcher.keys()
        if ks:
            models = Performance.query.filter(Event.id==Performance.event_id, Event.id.in_(self.event_fetcher.cached_keys()), Performance.backend_id.in_(ks)).all()
            fetcher.merge({m.backend_id: m for m in models})
        
        r = []
        for backend_id, (record, env) in self.performance_fetcher.data_iter:
            performance = fetcher.cache.get(backend_id)
            if performance is None:
                performance = fetcher.cache[backend_id] = Performance()
            try:
                if record.get("deleted"):
                    self.session.delete(performance) #need lazy?
                    continue
                r.append(performance)
                performance.backend_id = backend_id
                performance.event = self.event_fetcher.cache[env["event"]["id"]]
                performance.title = record['name']
                performance.venue = record['venue']
                performance.prefecture = PREFECTURES.get(record['prefecture'])
                performance.open_on = parse_datetime(record.get('open_on'))
                performance.start_on = parse_datetime(record['start_on'])
                performance.end_on = parse_datetime(record.get('end_on'))
            except KeyError as e:
                raise Exception("missing property '%s' in the performance record" % e.message)
        return r
        
    def fetch_salessegments(self, organization):
        fetcher = self.salessegment_fetcher
        ks = fetcher.keys()
        if ks:
            models = SalesSegment.query.filter(Performance.id==SalesSegment.performance_id, Performance.id.in_(self.performance_fetcher.cached_keys()), SalesSegment.backend_id.in_(ks)).all()
            fetcher.merge({m.backend_id: m for m in models})
        
        r = []

        salessegment_groups = SalesSegmentGroup.query.filter(SalesSegmentGroup.event_id.in_(self.event_fetcher.cached_keys()))
        group_dict = {(t.event_id, t.name, t.kind):t for t in salessegment_groups}

        for backend_id, (record, env) in self.salessegment_fetcher.data_iter:
            salessegment = fetcher.cache.get(backend_id)
            if salessegment is None:
                salessegment = fetcher.cache[backend_id] = SalesSegment()
            try:
                if record.get("deleted"):
                    self.session.delete(salessegment) #need lazy?
                    continue
                r.append(salessegment)
                salessegment.backend_id = backend_id
                salessegment.performance = self.performance_fetcher.cache[strict_get(env, "performance")["id"]]
                event = self.event_fetcher.cache[env["event"]["id"]]
                salessegment.group = group_dict.get((event.id, record["name"], record["kind"])) or SalesSegmentGroup(name=record["name"], kind=record["kind"], event_id=event.id)
                salessegment.start_on = parse_datetime(record['start_on'])
                salessegment.end_on = parse_datetime(record['end_on'])
            except KeyError as e:
                raise Exception("missing property '%s' in the salessegment record" % e.message)
        return r
        
    def fetch_tickets(self, organization):
        fetcher = self.ticket_fetcher
        ks = fetcher.keys()
        if ks:
            models = Ticket.query.filter(SalesSegment.id==Ticket.sale_id, SalesSegment.id.in_(self.performance_fetcher.cached_keys()), Ticket.backend_id.in_(ks)).all()
            fetcher.merge({m.backend_id: m for m in models})
        
        r = []
        for backend_id, (record, env) in self.ticket_fetcher.data_iter:
            ticket = fetcher.cache.get(backend_id)
            if ticket is None:
                ticket = fetcher.cache[backend_id] = Ticket()
            try:
                if record.get("deleted"):
                    self.session.delete(ticket) #need lazy?
                    continue
                r.append(ticket)
                ticket.backend_id = backend_id
                ticket.sale = self.salessegment_fetcher.cache[env["sale"]["id"]]
                ticket.name = record['name']
                ticket.price = record['price']
                ticket.seattype = record['seat_type']
            except KeyError as e:
                raise Exception("missing property '%s' in the ticket record" % e.message)
        return r


    def __call__(self, parsed):
        self.scan_toplevel(parsed)

        organization = self.fetch_organization(parsed)
        self.session.add(organization)
        self.session.flush()

        events = self.fetch_events(organization)
        self.session.add_all(events)
        self.session.flush()

        performances = self.fetch_performances(organization)
        self.session.add_all(performances)
        self.session.flush()

        salessegments = self.fetch_salessegments(organization)
        self.session.add_all(salessegments)
        self.session.flush()

        tickets = self.fetch_tickets(organization)
        self.session.add_all(tickets)
        self.session.flush()

        for action in self.after_parsed_actions:
            action()
        return events
