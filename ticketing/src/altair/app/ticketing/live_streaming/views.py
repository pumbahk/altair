# -*- coding:utf-8 -*-
from pyramid.view import view_config

from forms import LiveStreamingForm


@view_config(route_name="performances.live_streaming.edit", permission="authenticated",
             renderer='altair.app.ticketing:templates/performances/show.html',
             decorator="altair.app.ticketing.fanstatic.with_bootstrap",
             request_method="GET")
def live_streaming_edit_get(context, request):
    return dict(
        tab="live_streaming",
        performance=context.target,
        form=context.create_form()
    )


@view_config(route_name="performances.live_streaming.edit", permission="authenticated",
             renderer='altair.app.ticketing:templates/performances/show.html',
             decorator="altair.app.ticketing.fanstatic.with_bootstrap",
             request_method="POST")
def live_streaming_edit_post(context, request):
    performance = context.target
    form = LiveStreamingForm(request.POST)
    if form.validate():
        context.save_live_streaming_setting(form)
        request.session.flash(u'設定を保存しました')

    return dict(
        tab="live_streaming",
        performance=performance,
        form=form
    )
