from .models import FeatureSetting

class FeatureSettingManager:
    def __init__(self, request):
        self.organization_id = request.organization.id

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

def get_featuresettingmanager(request):
    return FeatureSettingManager(request)