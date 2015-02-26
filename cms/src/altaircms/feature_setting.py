from zope.interface import implementer, provider
from .models import FeatureSetting
from .interfaces import IFeatureSettingManager, IFeatureSettingManagerFactory

@implementer(IFeatureSettingManager)
@provider(IFeatureSettingManagerFactory)
class FeatureSettingManager(object):
    def __init__(self, request, organization_id):
        self.organization_id = organization_id

    def get_string_value(self, name, default_value = ""):
        """Get the FeatureSetting value as string.

        :param name: Name of the FeatureSetting to get
        :param default_value: Default value to return when FeatureSetting doesn't exist
        :return: Value of the FeatureSetting with the name for the request
        """

        str_value = FeatureSetting.get_value_by_name(organization_id=self.organization_id, name=name)
        if str_value is not None:
            return str_value
        else:
            return default_value

    def get_boolean_value(self, name, default_value = False):
        """Get the FeatureSetting value as boolean.

        :param name: Name of the FeatureSetting to get
        :param default_value: Default value to return when FeatureSetting doesn't exist, or the value is not "true" or "false"
        :return: Value of the FeatureSetting with the name for the request
        """

        str_value = self.get_string_value(name)
        if str_value.lower() == "true":
            return True
        elif str_value.lower() == "false":
            return False
        else:
            return default_value;

@provider(IFeatureSettingManagerFactory)
def cached_factory(request, organization_id):
    feature_setting_manager_cache = getattr(request, '__feature_setting_manager_cache', None)
    if feature_setting_manager_cache is None:
        feature_setting_manager_cache = request.__feature_setting_manager_cache = {}
    feature_setting_manager = feature_setting_manager_cache.get(organization_id)
    if feature_setting_manager is None:
        feature_setting_manager = feature_setting_manager_cache[organization_id] = FeatureSettingManager(request, organization_id)
    return feature_setting_manager

def includeme(config):
    config.registry.registerUtility(cached_factory, IFeatureSettingManagerFactory)
