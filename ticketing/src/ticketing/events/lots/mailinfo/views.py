# -*- coding:utf-8 -*-
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from ticketing.lots.models import LotEntry, Lot
from ticketing.core.models import Event
from ticketing.mails.api import get_mail_utility
from ..forms import SendingMailForm

@view_config(route_name="tickets.event.lots.mailinfo.preview", renderer="string")
def mail_preview(context, request):
    entry_id = request.matchdict['entry_id']
    organization_id = context.user.organization_id
    lot_entry = LotEntry.query.filter(LotEntry.lot_id==Lot.id, Lot.event_id==Event.id, Event.organization_id==organization_id,  LotEntry.id==entry_id).one()
    mutil = get_mail_utility(request, request.matchdict["mailtype"])
    return mutil.preview_text(request, (lot_entry, None))

@view_config(route_name="tickets.event.lots.mailinfo.send")
def send_mail(context, request):
    entry_id = request.matchdict['entry_id']
    organization_id = context.user.organization_id
    form = SendingMailForm(request.POST)
    if not form.validate():
        request.session.flash(u'失敗しました: %s' % form.errors)
        raise HTTPFound(request.current_route_url(entry_id=entry_id, action="show"))

    lot_entry = LotEntry.query.filter(LotEntry.lot_id==Lot.id, Lot.event_id==Event.id, Event.organization_id==organization_id,  LotEntry.id==entry_id).one()
    mutil = get_mail_utility(request, request.matchdict["mailtype"])
    mutil.send_mail(request, (lot_entry, None), override=form.data)

    request.session.flash(u'メール再送信しました')
    return HTTPFound(request.params.get("next_url") or "/")


