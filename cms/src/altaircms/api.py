from zope.interface import provider
from .interfaces import IFeatureSettingManagerFactory

def get_feature_setting_manager(request, organization_id):
    factory = request.registry.queryUtility(IFeatureSettingManagerFactory)
    return factory(request, organization_id)
