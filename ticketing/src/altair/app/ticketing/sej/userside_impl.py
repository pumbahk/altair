from zope.interface import implementer
from altair.app.ticketing.sej.api import merge_sej_tenant, get_default_sej_tenant
from altair.app.ticketing.sej.userside_interfaces import ISejTenantLookup
from altair.app.ticketing.core.models import SejTenant

@implementer(ISejTenantLookup)
class SejTenantLookup(object):
    def __init__(self):
        pass

    def __call__(self, request, organization_id):
        tenant = SejTenant.query.filter_by(organization_id=organization_id).one()
        return merge_sej_tenant(get_default_sej_tenant(request), tenant)

def includeme(config):
    config.registry.registerUtility(SejTenantLookup(), ISejTenantLookup)
