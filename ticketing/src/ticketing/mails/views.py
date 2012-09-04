from pyramid.view import view_config
from ticketing.fanstatic import with_bootstrap
from ticketing.mails.api import get_mail_utility
from ..core.models import Organization, Event, Performance

@view_config(route_name="mails.preview.organization", 
             decorator=with_bootstrap, permission="authenticated", 
             renderer="string")
def mail_preview_preorder_with_organization(context, request):
    mutil = get_mail_utility(request, request.matchdict["mailtype"])
    payment_id = request.params["payment_methods"]
    delivery_id = request.params["delivery_methods"]

    organization_id = int(request.matchdict.get("organization_id", 0))
    organization = Organization.get(organization_id)
    fake_order = mutil.create_fake_order(request, organization, payment_id, delivery_id)
    return mutil.preview_text(request, fake_order)

@view_config(route_name="mails.preview.event", 
             decorator=with_bootstrap, permission="authenticated", 
             renderer="string")
def mail_preview_preorder_with_event(context, request):
    mutil = get_mail_utility(request, request.matchdict["mailtype"])
    payment_id = request.params["payment_methods"]
    delivery_id = request.params["delivery_methods"]

    event_id = int(request.matchdict.get("event_id", 0))
    event = Event.get(event_id)
    fake_order = mutil.create_fake_order(request, event.organization, 
                                         payment_id, delivery_id, event=event)
    return mutil.preview_text(request, fake_order)

@view_config(route_name="mails.preview.performance", 
             decorator=with_bootstrap, permission="authenticated", 
             renderer="string")
def mail_preview_preorder_with_performance(context, request):
    mutil = get_mail_utility(request, request.matchdict["mailtype"])
    payment_id = request.params["payment_methods"]
    delivery_id = request.params["delivery_methods"]

    performance_id = int(request.matchdict.get("performance_id", 0))
    performance = Performance.get(performance_id)
    fake_order = mutil.create_fake_order(request, performance.event.organization,
                                         payment_id, delivery_id, performance=performance)
    return mutil.preview_text(request, fake_order)
