from zope.interface import provider
from .interfaces import (
    IFeatureSettingManagerFactory,
    ICMSPageURLAdapter,
    IBackendPageURLAdapter,
    ICartPageURLAdapter,
    ICMSMobilePageURLAdapter,
    ICMSSmartphonePageURLAdapter,
    ICMSPCPageURLAdapter,
    )

def get_hostname_from_request(request, qs=None, stage=None, default=None, preview=False):
    return request.host

def get_feature_setting_manager(request, organization_id):
    factory = request.registry.queryUtility(IFeatureSettingManagerFactory)
    return factory(request, organization_id)

def get_usersite_url_builder(request):
    return request.registry.queryUtility(ICMSPCPageURLAdapter)

def get_mobile_url_builder(request):
    return request.registry.queryUtility(ICMSMobilePageURLAdapter)

def get_smartphone_url_builder(request):
    return request.registry.queryUtility(ICMSSmartphonePageURLAdapter)

def get_backend_url_builder(request):
    return request.registry.queryUtility(IBackendPageURLAdapter)

def get_cms_url_builder(request):
    return request.registry.queryUtility(ICMSPageURLAdapter)

def get_cart_url_builder(request):
    return request.registry.queryUtility(ICartPageURLAdapter)

