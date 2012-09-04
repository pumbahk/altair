from pyramid.view import view_config, view_defaults
from ticketing.fanstatic import with_bootstrap
from ticketing.mails.api import get_mail_utility
from ..core.models import Organization

@view_config(route_name="mails.preview.organization", 
             decorator=with_bootstrap, permission="authenticated", 
             renderer="string")
def mail_preview_preorder(context, request):
    mutil = get_mail_utility(request, request.matchdict["mailtype"])
    payment_id = request.params["payment_methods"]
    delivery_id = request.params["delivery_methods"]
    organization_id = int(request.matchdict.get("organization_id", 0))
    organization = Organization.get(organization_id)
    fake_order = mutil.create_fake_order(request, organization, payment_id, delivery_id)
    return mutil.preview_text(request, fake_order)
