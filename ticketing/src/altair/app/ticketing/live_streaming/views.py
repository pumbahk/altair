# -*- coding:utf-8 -*-
from pyramid.view import view_config


@view_config(route_name="performances.live_streaming.show", permission="authenticated",
             renderer='altair.app.ticketing:templates/performances/show.html',
             decorator="altair.app.ticketing.fanstatic.with_bootstrap")
def live_streaming_show_get(context, request):

    performance = context.target

    return dict(
        tab="live_streaming",
        performance=performance,
    )
