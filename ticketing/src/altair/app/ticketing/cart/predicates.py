from .api import get_organization

def smartphone_enabled(request):
    organization = get_organization(request)
    return organization.setting.enable_smartphone_cart
