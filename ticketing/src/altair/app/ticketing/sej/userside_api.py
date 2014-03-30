from altair.app.ticketing.sej.userside_interfaces import ISejTenantLookup

def lookup_sej_tenant(request, organization_id):
    impl = request.registry.getUtility(ISejTenantLookup)
    return impl(request, organization_id)
