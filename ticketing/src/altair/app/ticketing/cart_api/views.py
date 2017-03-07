# -*- coding:utf-8 -*-
import logging

from pyramid.view import view_defaults, view_config
from pyramid.httpexceptions import HTTPNotFound

from altair.app.ticketing.cart.exceptions import OutTermSalesException

logger = logging.getLogger(__name__)


@view_defaults(renderer='json')
class CartAPIView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(route_name='cart.api.health_check')
    def health_check(self):
        return HTTPNotFound()

    @view_config(route_name='cart.api.index')
    def index(self):
        return dict(status='OK')

    @view_config(route_name='cart.api.performance')
    def performance(self):
        performance = self.context.performance
        if performance is None:
            return HTTPNotFound()
        # available_sales_segments = performance.sales_segments  # TODO: fix to available ss only
        try:
            available_sales_segments = self.context.available_sales_segments
        except OutTermSalesException as e:
            # FIXME: handle error when no sales segment is available
            logger.error("no sales segment available now: {}".format(self.context.now))
            raise HTTPNotFound()
        return dict(
            performance=dict(
                performance_id=performance.id,
                performance_name=performance.name,
                open_on=performance.open_on,
                start_on=performance.start_on,
                end_on=performance.end_on,
                order_limit=performance.setting.order_limit,
                venue_id=performance.venue.id,
                site_name=performance.venue.name
            ),
            event=dict(
                event_id=performance.event.id,
                order_limit=performance.event.setting.order_limit,
            ),
            sales_segments=[dict(
                sales_segment_id=ss.id,
                sales_segment_name=ss.sales_segment_group.name,
                start_at=ss.start_at,
                end_at=ss.end_at,
                seat_choice=ss.seat_choice,
                order_limit=ss.order_limit
            ) for ss in available_sales_segments]
        )
