# -*- coding:utf-8 -*-
from pyramid.view import view_config
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.mails.api import get_mail_utility
from ..core.models import Organization, Event, Performance
from . import forms

class ExtraMailInfoNotInitialized(Exception):
    def __init__(self, mutil, organization_id):
        self.mutil = mutil
        self.organization_id = organization_id

def check_initialized_or_not(request, mutil, fake_order):
    organization_id = request.context.user.organization_id
    if not mutil.get_traverser(request, fake_order).exists_at_least_one():
        raise ExtraMailInfoNotInitialized(mutil, organization_id)


@view_config(route_name="mails.preview.organization", 
             decorator=with_bootstrap, permission="authenticated", 
             renderer="altair.app.ticketing:templates/events/mailinfo/preview.html")
def mail_preview_preorder_with_organization(context, request):
    mutil = get_mail_utility(request, request.matchdict["mailtype"])
    payment_id = request.params["payment_methods"]
    delivery_id = request.params["delivery_methods"]
    organization_id = int(request.matchdict.get("organization_id", 0))
    organization = Organization.get(organization_id)
    fake_order = mutil.create_fake_order(request, organization, payment_id, delivery_id)
    check_initialized_or_not(request, mutil, fake_order)
    form = forms.MailInfoTemplate(request, organization, mutil=mutil).as_choice_formclass()(
        payment_methods=payment_id, 
        delivery_methods=delivery_id, 
        )
    return {"preview_text": mutil.preview_text(request, fake_order), 
            "mutil": mutil, "form": form}

@view_config(route_name="mails.preview.event", 
             decorator=with_bootstrap, permission="authenticated", 
             renderer="altair.app.ticketing:templates/events/mailinfo/preview.html")
def mail_preview_preorder_with_event(context, request):
    mutil = get_mail_utility(request, request.matchdict["mailtype"])
    payment_id = request.params["payment_methods"]
    delivery_id = request.params["delivery_methods"]

    event_id = int(request.matchdict.get("event_id", 0))
    event = Event.get(event_id)
    fake_order = mutil.create_fake_order(request, event.organization, 
                                         payment_id, delivery_id, event=event)
    check_initialized_or_not(request, mutil, fake_order)
    form = forms.MailInfoTemplate(request, event.organization, mutil=mutil).as_choice_formclass()(
        payment_methods=payment_id, 
        delivery_methods=delivery_id, 
        )
    return {"preview_text": mutil.preview_text(request, fake_order), 
            "mutil": mutil, "form": form}

@view_config(route_name="mails.preview.performance", 
             decorator=with_bootstrap, permission="authenticated", 
             renderer="altair.app.ticketing:templates/events/mailinfo/preview.html")
def mail_preview_preorder_with_performance(context, request):
    mutil = get_mail_utility(request, request.matchdict["mailtype"])
    payment_id = request.params["payment_methods"]
    delivery_id = request.params["delivery_methods"]

    performance_id = int(request.matchdict.get("performance_id", 0))
    performance = Performance.get(performance_id, context.user.organization_id)
    fake_order = mutil.create_fake_order(request, performance.event.organization,
                                         payment_id, delivery_id, performance=performance)
    check_initialized_or_not(request, mutil, fake_order)
    form = forms.MailInfoTemplate(request, performance.event.organization, mutil=mutil).as_choice_formclass()(
        payment_methods=payment_id, 
        delivery_methods=delivery_id, 
        )
    return {"preview_text": mutil.preview_text(request, fake_order), 
            "mutil": mutil, "form": form}

@view_config(route_name="mails.preview.organization", 
             decorator=with_bootstrap, context=ExtraMailInfoNotInitialized,
             renderer="altair.app.ticketing:templates/events/mailinfo/preview_failure.html")
@view_config(route_name="mails.preview.event", 
             decorator=with_bootstrap, context=ExtraMailInfoNotInitialized,
             renderer="altair.app.ticketing:templates/events/mailinfo/preview_failure.html")
@view_config(route_name="mails.preview.performance", 
             decorator=with_bootstrap, context=ExtraMailInfoNotInitialized,
             renderer="altair.app.ticketing:templates/events/mailinfo/preview_failure.html")
def mail_preview_failed(context, request):
    return {"mutil":context.mutil, 
            "organization_id": context.organization_id, 
            "mailtype": context.mutil.mtype}
