from zope.interface import Interface

class ISejTenantLookup(Interface):
    def __call__(request, organization_id):
        pass
