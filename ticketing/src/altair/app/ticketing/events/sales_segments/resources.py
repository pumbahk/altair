# -*- coding: utf-8 -*-

from pyramid.httpexceptions import HTTPNotFound
from sqlalchemy.orm.exc import NoResultFound

from altair.app.ticketing.resources import TicketingAdminResource
from altair.app.ticketing.core.models import SalesSegment, SalesSegmentGroup, Performance, Event, Organization, PaymentDeliveryMethodPair

class SalesSegmentAdminResource(TicketingAdminResource):
    def __init__(self, request):
        super(SalesSegmentAdminResource, self).__init__(request)

        event_id = None
        sales_segment_id = None
        sales_segment_group_id = None
        performance_id = None

        if not self.user:
            return

        try:
            event_id = long(self.request.matchdict.get('event_id'))
        except (TypeError, ValueError):
            pass

        try:
            sales_segment_id = long(self.request.matchdict.get('sales_segment_id'))
        except (TypeError, ValueError):
            pass

        try:
            sales_segment_group_id = long(self.request.params.get('sales_segment_group_id'))
        except (TypeError, ValueError):
            pass

        try:
            performance_id = long(self.request.params.get('performance_id'))
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

        if performance_id is not None:
            try:
                self.performance = Performance.query \
                    .join(Performance.event) \
                    .join(Event.organization) \
                    .filter(Organization.id == self.user.organization_id) \
                    .filter(Performance.id == performance_id) \
                    .one()
            except NoResultFound:
                self.performance = None

            if self.performance is None or \
               (self.event is not None and \
                self.performance.event_id != self.event.id):
                raise HTTPNotFound()
            if self.event is None:
                self.event = self.performance.event
        else:
            self.performance = None

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

        if sales_segment_id is not None:
            try:
                self.sales_segment = SalesSegment.query \
                    .join(SalesSegment.sales_segment_group) \
                    .join(SalesSegmentGroup.event) \
                    .join(Event.organization) \
                    .filter(Organization.id == self.user.organization_id) \
                    .filter(SalesSegment.id == sales_segment_id) \
                    .one()
            except NoResultFound:
                self.sales_segment = None

            if self.sales_segment is None or \
               (self.sales_segment_group is not None and \
                self.sales_segment.sales_segment_group_id != self.sales_segment_group.id) or \
               (self.performance is not None and \
                self.sales_segment.performance_id != self.performance.id):
                raise HTTPNotFound()
            if self.sales_segment_group is None:
                self.sales_segment_group = self.sales_segment.sales_segment_group
            if self.event is None:
                self.event = self.sales_segment_group.event
            if self.performance is None:
                self.performance = self.sales_segment.performance
        else:
            self.sales_segment = None

class SalesSegmentEditor(object):
    use_default_fields = [
        "seat_choice",
        "public",
        "reporting",
        "payment_delivery_method_pairs",
        "start_at",
        "end_at",
        "upper_limit",
        "order_limit",
        "account_id",
        "margin_ratio",
        "refund_ratio",
        "printing_fee",
        "registration_fee",
        "auth3d_notice",
    ]

    def __init__(self, sales_segment_group, form):
        self.sales_segment_group = sales_segment_group
        self.form = form

    def apply_changes(self, obj):
        for field in self.form:
            if field.name == "payment_delivery_method_pairs":
                value = self.get_value(field, obj.performance)
                if any([isinstance(v, int) for v in value]):
                    value = PaymentDeliveryMethodPair.query.filter(
                        PaymentDeliveryMethodPair.id.in_(value)).all()
                setattr(obj, field.name, value)
            else:
                setattr(obj, field.name, self.get_value(field, obj.performance))
        return obj

    def is_use_default(self, field):
        return self.form["use_default_" + field.name].data

    def get_value(self, field, performance):
        if field.name not in self.use_default_fields:
            return field.data
        else:
            if not self.is_use_default(field):
                return field.data
            else:
                if field.name == 'start_at':
                    return self.sales_segment_group.start_for_performance(performance)
                elif field.name == 'end_at':
                    return self.sales_segment_group.end_for_performance(performance)
                else:
                    return getattr(self.sales_segment_group, field.name)




def sync_attr(dest, src, attr):
    setattr(dest, attr, getattr(src, attr))

class SalesSegmentGroupCreate(object):
    def __init__(self, new_sales_segment_group):
        self.ssg = new_sales_segment_group

    def create(self, performances):
        for p in performances:
            self.create_sales_segment_for(p)

    def create_sales_segment_for(self, performance):
        ss = SalesSegment(
            organization=performance.event.organization,
            event=performance.event,
            performance=performance,
            sales_segment_group=self.ssg,
            use_default_seat_choice=True,
            use_default_public=True,
            use_default_reporting=True,
            use_default_payment_delivery_method_pairs=True,
            use_default_start_at=True,
            use_default_end_at=True,
            use_default_upper_limit=True,
            use_default_order_limit=True,
            use_default_account_id=True,
            use_default_margin_ratio=True,
            use_default_refund_ratio=True,
            use_default_printing_fee=True,
            use_default_registration_fee=True,
            use_default_auth3d_notice=True,
            )
        update_sales_segment(self.ssg, ss)
        return ss

    def create_sales_lot_segment(self, lot):
        ss = SalesSegment(
            organization=lot.event.organization,
            event=lot.event,
            sales_segment_group=self.ssg,
            use_default_seat_choice=True,
            use_default_public=True,
            use_default_reporting=True,
            use_default_payment_delivery_method_pairs=True,
            use_default_start_at=True,
            use_default_end_at=True,
            use_default_upper_limit=True,
            use_default_order_limit=True,
            use_default_account_id=True,
            use_default_margin_ratio=True,
            use_default_refund_ratio=True,
            use_default_printing_fee=True,
            use_default_registration_fee=True,
            use_default_auth3d_notice=True,
            )
        lot.sales_segment = ss
        update_sales_segment(self.ssg, ss)
        return ss
            
class SalesSegmentGroupUpdate(object):

    def __init__(self, sales_segment_group):
        self.ssg = sales_segment_group

    def update(self, sales_segments):
        for ss in sales_segments:
            update_sales_segment(self.ssg, ss)

def update_sales_segment(ssg, ss):
    if ss.use_default_start_at:
        ss.start_at = ssg.start_for_performance(ss.performance)
    if ss.use_default_end_at:
        ss.end_at = ssg.end_for_performance(ss.performance)
    if ss.use_default_seat_choice:
        sync_attr(ss, ssg, 'seat_choice')
    if ss.use_default_public:
        sync_attr(ss, ssg, 'public')
    if ss.use_default_reporting:
        sync_attr(ss, ssg, 'reporting')
    if ss.use_default_payment_delivery_method_pairs:
        sync_attr(ss, ssg, 'payment_delivery_method_pairs')
    if ss.use_default_upper_limit:
        sync_attr(ss, ssg, 'upper_limit')
    if ss.use_default_order_limit:
        sync_attr(ss, ssg, 'order_limit')
    if ss.use_default_account_id:
        sync_attr(ss, ssg, 'account_id')
    if ss.use_default_margin_ratio:
        sync_attr(ss, ssg, 'margin_ratio')
    if ss.use_default_refund_ratio:
        sync_attr(ss, ssg, 'refund_ratio')
    if ss.use_default_printing_fee:
        sync_attr(ss, ssg, 'printing_fee')
    if ss.use_default_registration_fee:
        sync_attr(ss, ssg, 'registration_fee')
    if ss.use_default_auth3d_notice:
        sync_attr(ss, ssg, 'auth3d_notice')

