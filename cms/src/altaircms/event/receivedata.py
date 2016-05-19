# coding: utf-8
import logging
logger = logging.getLogger(__name__)
import isodate
from altaircms.event.models import Event
from altaircms.auth.models import Organization
from altaircms.models import Performance, SalesSegment, Ticket, SalesSegmentGroup, SalesSegmentKind
from altaircms.seeds.prefecture import PREFECTURE_CHOICES
from . import subscribers
from ..modelmanager import SalesTermSummalize
from ..modelmanager import EventTermSummalize

def parse_datetime(dtstr):
    if dtstr is None or dtstr == "":
        return None
    try:
        return isodate.parse_datetime(dtstr)
    except ValueError, e:
        logger.warn(str(e))
        raise InvalidParamaterException("Invalid ISO8601 datetime: %s" % dtstr)

ORGANIZATION_SOURCE = "oauth" #todo backend api include this

class InvalidParamaterException(Exception):
    pass

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
        raise InvalidParamaterException(msg % k)
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
        organization.code = record.get("code")
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
                    del fetcher.cache[backend_id]
                    self.session.delete(event) #need lazy?
                    continue
                r.append(event)
                event.backend_id = backend_id
                event.title = record['title']
                event.subtitle = record.get('subtitle', '')
                ## 自動で計算
                # event.event_open = parse_datetime(record['start_on'])
                # event.event_close = parse_datetime(record['end_on'])
                # event.deal_open = parse_datetime(record.get('deal_open'))
                # event.deal_close = parse_datetime(record.get('deal_close'))
                event.code = record['code']
                event.organization_id = organization.id
                def notify_event_update():
                    subscribers.notify_event_update(self.request, event)
                self.after_parsed_actions.append(notify_event_update)
            except KeyError as e:
                raise InvalidParamaterException("missing property '%s' in the event record" % e.message)
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
            try:
                if record.get("deleted"):
                    if performance:
                        del fetcher.cache[backend_id]
                        self.session.delete(performance) #need lazy?
                    continue
                if performance is None:
                    performance = fetcher.cache[backend_id] = Performance()
                r.append(performance)
                performance.backend_id = backend_id
                try:
                    performance.event = self.event_fetcher.cache[env["event"]["id"]]
                except KeyError:
                    if self.performance.id:
                        self.session.delete(performance)
                    logger.info("parent element is deleted. so,  this object also deleted(backend_id=%s)" % (backend_id))
                    r.pop()
                    continue
                performance.title = record['name']
                performance.venue = record['venue']
                performance.prefecture = PREFECTURES.get(record['prefecture'])
                performance.display_order = record.get("display_order", 50)
                performance.open_on = parse_datetime(record.get('open_on'))
                performance.start_on = parse_datetime(record['start_on'])
                performance.end_on = parse_datetime(record.get('end_on'))
                performance.code = record.get('code')
                performance.public = record.get('public')
                performance.display_order = record.get('display_order')
                performance.purchase_link = record.get('purchase_link')
                performance.mobile_purchase_link = record.get('mobile_purchase_link')
            except KeyError as e:
                raise InvalidParamaterException("missing property '%s' in the performance record" % e.message)
        return r

    def _retrive_salessegment_group(self, organization, event, salessegment, record, group_dict, group_failback_dict, kind_dict):
        kind_name = record.get("kind_name", "unknown")
        publicp = record.get("group_publicp")
        salessegment.group = group_dict.get((event.id, record.get("group_id"))) or group_failback_dict.get((event.id, record["name"], kind_name, publicp))
        if salessegment.group is None:
            if record.get("group_id"):
                salessegment.group = group_dict[(event.id, record.get("group_id"))] = SalesSegmentGroup(name=record["name"], kind=kind_name, event_id=event.id)
            else:
                logger.warn("group id is not found: {0}. creating it.".format(record))
                salessegment.group = group_failback_dict[(event.id, record["name"], kind_name)] = SalesSegmentGroup(name=record["name"], kind=kind_name, event_id=event.id, publicp=publicp)
        salessegment.group.backend_id = record.get("group_id")

        salessegment.kind = kind_name

        kind = kind_dict.get(kind_name, None)
        if kind is None:
            kind = kind_dict[kind_name] =  SalesSegmentKind(name=kind_name, organization_id=organization.id)
        kind.label = record.get("kind_label", u"<不明>")
        salessegment.group.master = kind
        salessegment.group.kind = kind.name #todo:replace
        salessegment.group.publicp = publicp

    def fetch_salessegments(self, organization):
        fetcher = self.salessegment_fetcher
        ks = fetcher.keys()
        if ks:
            models = SalesSegment.query.filter(Performance.id==SalesSegment.performance_id, Performance.id.in_(self.performance_fetcher.cached_keys()), SalesSegment.backend_id.in_(ks)).all()
            fetcher.merge({m.backend_id: m for m in models})
        
        r = []

        salessegment_groups = SalesSegmentGroup.query.filter(SalesSegmentGroup.event_id.in_(self.event_fetcher.cached_keys()))

        group_dict = {(t.event_id, t.backend_id):t for t in salessegment_groups}
        group_failback_dict = {(t.event_id, t.name, t.kind):t for t in salessegment_groups}
        salessegmen_kinds = SalesSegmentKind.query.filter(SalesSegmentKind.organization_id == organization.id)
        kind_dict = {k.name: k for k in salessegmen_kinds}

        for backend_id, (record, env) in self.salessegment_fetcher.data_iter:
            salessegment = fetcher.cache.get(backend_id)
            try:
                if record.get("deleted"):
                    if salessegment:
                        self.session.delete(salessegment) #need lazy?
                        del fetcher.cache[backend_id]
                    continue
                if salessegment is None:
                    salessegment = fetcher.cache[backend_id] = SalesSegment()
                r.append(salessegment)
                salessegment.backend_id = backend_id
                try:
                    salessegment.performance = self.performance_fetcher.cache[strict_get(env, "performance")["id"]]
                except KeyError:
                    if salessegment.id:
                        self.session.delete(salessegment)
                    logger.info("parent element is deleted. so,  this object also deleted(backend_id=%s)" % (backend_id))
                    r.pop()
                    continue
                event = self.event_fetcher.cache[env["event"]["id"]]              
                salessegment.start_on = parse_datetime(record['start_on'])
                salessegment.end_on = parse_datetime(record['end_on'])
                salessegment.publicp = record['publicp']
                ## kind, group
                self._retrive_salessegment_group(organization, event, salessegment, record, group_dict, group_failback_dict, kind_dict)
            except KeyError as e:
                raise InvalidParamaterException("missing property '%s' in the salessegment record" % e.message)
        for g in group_dict.values():
            if not g.salessegments:
                self.session.delete(g)
        return r
        
    def fetch_tickets(self, organization):
        fetcher = self.ticket_fetcher
        ks = fetcher.keys()
        if ks:
            models = Ticket.query.filter(SalesSegment.id==Ticket.sale_id, SalesSegment.id.in_(self.salessegment_fetcher.cached_keys()), Ticket.backend_id.in_(ks)).all()
            fetcher.merge({m.backend_id: m for m in models})
        
        r = []
        for backend_id, (record, env) in self.ticket_fetcher.data_iter:
            ticket = fetcher.cache.get(backend_id)
            try:
                if record.get("deleted"):
                    if ticket:
                        del fetcher.cache[backend_id]
                        self.session.delete(ticket) #need lazy?
                    continue
                if ticket is None:
                    ticket = fetcher.cache[backend_id] = Ticket()
                r.append(ticket)
                ticket.backend_id = backend_id
                try:
                    ticket.sale = self.salessegment_fetcher.cache[env["sale"]["id"]]
                except KeyError:
                    if ticket.id:
                        self.session.delete(ticket)
                    logger.info("parent element is deleted. so,  this object also deleted(backend_id=%s)" % (backend_id))
                    r.pop()
                    continue
                ticket.name = record['name']
                ticket.price = record['price']
                ticket.display_order = record.get("display_order") or 50
                ticket.seattype = record['seat_type'] or ""
            except KeyError as e:
                raise InvalidParamaterException("missing property '%s' in the ticket record" % e.message)
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

        ssum = SalesTermSummalize(self.request)        
        esum = EventTermSummalize(self.request)        
        for event in events:
            ssum.summalize(event).term()
            esum.summalize(event).term()

        for action in self.after_parsed_actions:
            action()
        return events
