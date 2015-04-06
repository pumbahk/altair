# -*- coding: utf-8 -*-

from pyramid.httpexceptions import HTTPNotFound
from sqlalchemy.orm.exc import NoResultFound
import logging

from zope.interface import Interface, Attribute, implementer
from altair.app.ticketing.resources import TicketingAdminResource
from altair.app.ticketing.core.models import SalesSegment, SalesSegmentGroup, SalesSegmentSetting, SalesSegmentGroupSetting, Performance, Event, Organization, PaymentDeliveryMethodPair
from altair.app.ticketing.utils import DateTimeRange

logger = logging.getLogger(__name__)

class ISalesSegmentAdminResource(Interface):
    event = Attribute('')
    performance = Attribute('')
    sales_segment_group = Attribute('')
    sales_segment = Attribute('')

@implementer(ISalesSegmentAdminResource)
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
            self.sales_segment_range = DateTimeRange(self.sales_segment.start_at, self.sales_segment.end_at)
            if self.sales_segment_group is None:
                self.sales_segment_group = self.sales_segment.sales_segment_group
            if self.event is None:
                self.event = self.sales_segment_group.event
            if self.performance is None:
                self.performance = self.sales_segment.performance
        else:
            self.sales_segment = None

class SalesSegmentAccessor(object):
    attributes = {
        "start_at": dict(
            getter=lambda sales_segment_group, performance: sales_segment_group.start_for_performance(performance),
            has_use_default=True,
            use_default_default=True,
            use_default_default_for_lot=False
            ),
        "end_at": dict(
            getter=lambda sales_segment_group, performance: sales_segment_group.end_for_performance(performance),
            has_use_default=True,
            use_default_default=True,
            use_default_default_for_lot=False
            ),
        "seat_choice": dict(
            has_use_default=True,
            use_default_default=True,
            use_default_default_for_lot=False
            ),
        "display_seat_no": dict(
            setting=True,
            has_use_default=True,
            use_default_default=True,
            use_default_default_for_lot=False
            ),
        "public": dict(
            has_use_default=True,
            use_default_default=True
            ),
        "reporting": dict(
            has_use_default=True,
            use_default_default=True
            ),
        "sales_counter_selectable": dict(
            setting=True,
            has_use_default=True,
            use_default_default=True
            ),
        "payment_delivery_method_pairs": dict(
            has_use_default=True,
            use_default_default=True
            ),
        "max_quantity": dict(
            has_use_default=True,
            use_default_default=True,
            use_default_default_for_lot=False
            ),
        "max_product_quatity": dict(
            has_use_default=True,
            use_default_default=True,
            use_default_default_for_lot=False
            ),
        "account_id": dict(
            has_use_default=True,
            use_default_default=True
            ),
        "margin_ratio": dict(
            has_use_default=True,
            use_default_default=True
            ),
        "refund_ratio": dict(
            has_use_default=True,
            use_default_default=True
            ),
        "printing_fee": dict(
            has_use_default=True,
            use_default_default=True
            ),
        "registration_fee": dict(
            has_use_default=True,
            use_default_default=True
            ),
        "auth3d_notice": dict(
            has_use_default=True,
            use_default_default=True
            ),
        "order_limit": dict(
            setting=True,
            has_use_default=True,
            use_default_default=True
            ),
        "max_quantity_per_user": dict(
            setting=True,
            has_use_default=True,
            use_default_default=True
            ),
        "disp_orderreview": dict(
            setting=True,
            has_use_default=True,
            use_default_default=True
            ),
        "disp_agreement": dict(
            setting=True,
            has_use_default=True,
            use_default_default=True
            ),
        "agreement_body": dict(
            setting=True,
            has_use_default=True,
            use_default_default=True
            ),
        "extra_form_fields": dict(
            setting=True,
            has_use_default=True,
            use_default_default=True
            )
        }

    setting_attributes = set(k for k, desc in attributes.items() if desc.get('setting', False))

    def sync_attr(self, dest, src, attr):
        self.attr_set(dest, attr, self.attr_get(src, attr))

    def attr_set(self, obj, name, value):
        if self.attributes.get(name).get('setting'):
            setattr(obj.setting, name, value)
        else:
            setattr(obj, name, value)

    def attr_get(self, obj, name):
        if self.attributes.get(name).get('setting'):
            return getattr(obj.setting, name)
        else:
            return getattr(obj, name)

    def set_use_default(self, obj, name, value):
        if not self.attributes.get(name).get('has_use_default'):
            return False
        if self.attributes.get(name).get('setting'):
            setattr(obj.setting, 'use_default_%s' % name, value)
        else:
            setattr(obj, 'use_default_%s' % name, value)
        return True

    def get_use_default(self, obj, name):
        if not self.attributes.get(name).get('has_use_default'):
            return False
        if self.attributes.get(name).get('setting'):
            return getattr(obj.setting, 'use_default_%s' % name)
        else:
            return getattr(obj, 'use_default_%s' % name)

    def attr_get_default(self, sales_segment_group, performance, name):
        getter = self.attributes[name].get('getter')
        if getter is not None and performance is not None:
            return getter(sales_segment_group, performance)
        else:
            return self.attr_get(sales_segment_group, name)

    def update_sales_segment(self, sales_segment):
        if sales_segment.setting is None:
            sales_segment.setting = SalesSegmentSetting()
        for k in self.attributes.keys():
            if self.get_use_default(sales_segment, k):
                default_value = self.attr_get_default(
                    sales_segment.sales_segment_group,
                    sales_segment.performance,
                    k)
                logger.debug('sales_segment(id=%r).%s set to default value %r' % (sales_segment.id, k, default_value))
                self.attr_set(sales_segment, k, default_value)

    def create_sales_segment_for_performance(self, sales_segment_group, performance):
        ss = SalesSegment(
            organization=performance.event.organization,
            event=performance.event,
            performance=performance,
            sales_segment_group=sales_segment_group,
            membergroups=list(sales_segment_group.membergroups),
            setting=SalesSegmentSetting(
                **dict(
                    (
                        'use_default_%s' % k,
                        desc.get('use_default_default', False)
                        )
                    for k, desc in self.attributes.items()
                    if desc.get('has_use_default') and desc.get('setting')
                    )
                ),
            **dict(
                (
                    'use_default_%s' % k,
                    desc.get('use_default_default', False)
                    )
                for k, desc in self.attributes.items()
                if desc.get('has_use_default') and not desc.get('setting')
                )
            )
        self.update_sales_segment(ss)
        return ss

    def create_sales_segment_for_lot(self, sales_segment_group, lot):
        ss = SalesSegment(
            organization=lot.event.organization,
            event=lot.event,
            sales_segment_group=sales_segment_group,
            membergroups=list(sales_segment_group.membergroups),
            setting=SalesSegmentSetting(
                **dict(
                    (
                        'use_default_%s' % k,
                        desc.get('use_default_default', False)
                        )
                    for k, desc in self.attributes.items()
                    if desc.get('has_use_default') and desc.get('setting')
                    )
                ),
            **dict(
                (
                    'use_default_%s' % k,
                    desc.get('use_default_default', False)
                    )
                for k, desc in self.attributes.items()
                if desc.get('has_use_default') and not desc.get('setting')
                )
            )
        lot.sales_segment = ss
        self.update_sales_segment(ss)
        return ss


class SalesSegmentEditor(object):
    def __init__(self, sales_segment_group, form):
        self.sales_segment_group = sales_segment_group
        self.form = form
        self.accessor = SalesSegmentAccessor()

    def apply_changes(self, obj):
        for k, desc in self.accessor.attributes.items():
            field = getattr(self.form, k)
            if k == "payment_delivery_method_pairs":
                value = self.get_value(k, obj.performance)
                if any([isinstance(v, int) for v in value]):
                    value = PaymentDeliveryMethodPair.query.filter(
                        PaymentDeliveryMethodPair.id.in_(value)).all()
                self.accessor.attr_set(obj, k, value)
            else:
                self.accessor.attr_set(obj, k, self.get_value(k, obj.performance))
            if desc.get('has_use_default'):
                use_default_field = getattr(self.form, 'use_default_%s' % k, None)
                if use_default_field is not None:
                    self.accessor.set_use_default(obj, k, use_default_field.data)
                else:
                    logger.warning("field `use_default_%s' does not exist!" % k)
        return obj

    def get_value(self, k, performance):
        desc = self.accessor.attributes.get(k)
        use_default = desc.get('has_use_default') and self.form["use_default_" + k].data
        if use_default:
            return self.accessor.attr_get_default(self.sales_segment_group, performance, k)
        else:
            return self.form[k].data
