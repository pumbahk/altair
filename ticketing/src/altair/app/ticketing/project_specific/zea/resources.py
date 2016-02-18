import re
from pyramid.decorator import reify
from zope.interface import implementer
from altair.sqlahelper import get_db_session
from altair.app.ticketing.core.models import Event, Performance, SalesSegment, SalesSegmentGroup
from altair.app.ticketing.orders.models import Order

from .interfaces import IFCAdminSettings

class FCAdminResourceBase(object):
    @reify
    def slave_db_session(self):
        return get_db_session(self.request, 'slave')

class FCAdminEventIndexResource(FCAdminResourceBase):
    def __init__(self, request):
        self.request = request

    @reify
    def events(self):
        event_ids = get_fc_admin_settings(self.request).event_ids
        return self.slave_db_session.query(Event) \
            .filter(Event.id.in_(event_ids)) \
            .all()

    def __getitem__(self, event_id):
        try:
            event_id = long(event_id)
        except (TypeError, ValueError):
            event_id = None
        event_ids = get_fc_admin_settings(self.request).event_ids
        if event_id not in event_ids:
            raise KeyError(event_id)
        return FCAdminEventResource(
            self.request,
            event_id
            )
             

class FCAdminEventResource(FCAdminResourceBase):
    def __init__(self, request):
        self.request = request
        self.event_id = request.matchdict['event_id']

    @reify
    def event(self):
        return self.slave_db_session.query(Event).filter_by(id=self.event_id).one()

    @property
    def orders(self):
        return self.slave_db_session.query(Order) \
            .join(Order.sales_segment) \
            .join(SalesSegment.sales_segment_group) \
            .filter(SalesSegmentGroup.event_id == self.event_id)

    @property
    def canceled_orders(self):
        return self.orders.filter(Order.canceled_at != None)

    @property
    def valid_orders(self):
        return self.orders.filter(Order.canceled_at == None)

    @property
    def paid_orders(self):
        return self.valid_orders.filter(Order.paid_at != None)


def root_factory(request):
    return FCAdminEventIndexResource(request)


def get_fc_admin_settings(request_or_registry):
    if hasattr(request_or_registry, 'registry'):
        registry = request_or_registry.registry
    else:
        registry = request_or_registry
    return registry.queryUtility(IFCAdminSettings)


@implementer(IFCAdminSettings)
class FCAdminSettings(object):
    def __init__(self, event_ids):
        self.event_ids = event_ids


def includeme(config):
    import ipdb;ipdb.set_trace()
    config.registry.registerUtility(
        FCAdminSettings(
            event_ids=[
                long(v.strip())
                for v in re.split(
                    ur'\s+|,',
                    config.registry.settings['altair.zea_admin.events']
                    )
                ],
            ),
        IFCAdminSettings
        )

