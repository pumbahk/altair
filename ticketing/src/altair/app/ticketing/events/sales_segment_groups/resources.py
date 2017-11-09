from pyramid.httpexceptions import HTTPNotFound
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.util import class_mapper
from sqlalchemy import sql

from altair.sqla import new_comparator

from altair.app.ticketing.resources import TicketingAdminResource
from altair.app.ticketing.core.models import SalesSegment, SalesSegmentGroup, Performance, Event, Organization, PaymentDeliveryMethodPair
from altair.app.ticketing.lots.models import Lot
from .forms import CopyLotForm

class SalesSegmentGroupAdminResource(TicketingAdminResource):
    def __init__(self, request):
        super(SalesSegmentGroupAdminResource, self).__init__(request)

        event_id = None
        sales_segment_group_id = None

        if not self.user:
            return

        try:
            event_id = long(self.request.matchdict.get('event_id'))
        except (TypeError, ValueError):
            pass

        try:
            sales_segment_group_id = long(self.request.matchdict.get('sales_segment_group_id'))
        except (TypeError, ValueError):
            pass

        if event_id is not None:
            try:
                self.event = Event.query \
                    .join(Event.organization) \
                    .filter(Organization.id == self.user.organization_id) \
                    .filter(Event.id == event_id) \
                    .one()
            except NoResultFound:
                raise HTTPNotFound()
        else:
            self.event = None

        if sales_segment_group_id is not None:
            try:
                self.sales_segment_group = SalesSegmentGroup.query \
                    .join(SalesSegmentGroup.event) \
                    .join(Event.organization) \
                    .filter(Organization.id == self.user.organization_id) \
                    .filter(SalesSegmentGroup.id == sales_segment_group_id) \
                    .one()
            except NoResultFound:
                self.sales_segment_group = None

            if self.sales_segment_group is None or \
               (self.event is not None and \
                self.sales_segment_group.event_id != self.event.id):
                raise HTTPNotFound()
            if self.event is None:
                self.event = self.sales_segment_group.event
        else:
            self.sales_segment_group = None

    @property
    def lot(self):
        lot_id = self.request.matchdict.get('lot_id')
        return Lot.query.filter(Lot.id == lot_id).first()

    def sort_sales_segment(self):
        sort_column = self.request.GET.get('sort')
        query = SalesSegment.query.filter(SalesSegment.sales_segment_group_id == self.request.matchdict.get('sales_segment_group_id'))

        if sort_column == 'start_on':
            query = query.join(Performance)
            md_class = Performance
        else:
            md_class = SalesSegment
        try:
            mapper = class_mapper(md_class)
            prop = mapper.get_property(sort_column)
            sort = new_comparator(prop, mapper)
        except:
            sort = None
        direction = {'asc': sql.asc, 'desc': sql.desc}.get(
            self.request.GET.get('direction'),
            sql.asc
        )
        self.sales_segment_group.sales_segments = query.order_by(direction(sort)).all()
        return None