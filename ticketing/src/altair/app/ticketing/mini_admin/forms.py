# -*- coding: utf-8 -*-

import logging

from altair.app.ticketing.core.models import (
    SalesSegmentGroup,
    Performance,
    Event,
)
from altair.viewhelpers.datetime_ import create_date_time_formatter, DateTimeHelper

from ..orders.forms import OrderSearchForm

logger = logging.getLogger(__name__)


class MiniAdminOrderSearchForm(OrderSearchForm):
    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        super(MiniAdminOrderSearchForm, self).__init__(formdata, **kwargs)

        if self.event_id.data:

            dthelper = DateTimeHelper(create_date_time_formatter(self.request))
            performances = Performance.query.join(Event) \
                .filter(Event.id == self.event_id.data) \
                .order_by(Performance.created_at.desc())
            self.performance_id.choices = [('', u'')] + [
                (p.id, '%s (%s)' % (p.name, dthelper.datetime(p.start_on, with_weekday=True))) for p in
                performances]

            sales_segment_groups = SalesSegmentGroup.query.filter(SalesSegmentGroup.event_id == self.event_id.data)
            self.sales_segment_group_id.choices = [(sales_segment_group.id, sales_segment_group.name) for
                                                   sales_segment_group in sales_segment_groups]
