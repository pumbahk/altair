from pyramid.httpexceptions import HTTPNotFound
from sqlalchemy.orm.exc import NoResultFound

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
        return Lot.query.filter(Lot.id==lot_id).first()

    def create_lot_copy_form(self, context, new_form):
        form = CopyLotForm(None, context=context, new_form=new_form)
        if self.lot:
            sales_segment_group = self.lot.sales_segment.sales_segment_group

            form.sales_segment_group.data = sales_segment_group
            form.lot.data = self.lot

            form.lot_name.data = self.lot.name
            form.limit_wishes.data = self.lot.limit_wishes
            form.entry_limit.data = self.lot.entry_limit
            form.description.data = self.lot.description
            form.lotting_announce_datetime.data = self.lot.lotting_announce_datetime
            form.lotting_announce_timezone.data = self.lot.lotting_announce_timezone
            form.custom_timezone_label.data = self.lot.custom_timezone_label
            form.auth_type.data = self.lot.auth_type
        return form

    def create_lot_copy_form_with_form_data(self, context):
        form = CopyLotForm(self.request.POST, context=context)
        form.lot.data = self.lot
        form.sales_segment_group.data = self.lot.sales_segment.sales_segment_group
        return form
