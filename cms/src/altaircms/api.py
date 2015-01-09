from .models import FeatureSetting

class FeatureSettingManager:
    def __init__(self, request):
        self.organization_id = request.organization.id

    def get_string_value(self, name, default_value = ""):
        str_value = FeatureSetting.get_value_by_name(organization_id=self.organization_id, name=name)
        if str_value is not None:
            return str_value
        else:
            return default_value

    def get_boolean_value(self, name, default_value = False):
        str_value = self.get_string_value(name)
        if str_value is not None and str_value.lower() == "true":
            return True
        else:
            return default_value;

def get_featuresettingmanager(request):
    return FeatureSettingManager(request)