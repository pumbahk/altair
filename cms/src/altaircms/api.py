from .models import FeatureSetting

class FeatureSettingManager:
    def __init__(self, request):
        self.organization = request.organization

    def get_boolean_value(self, name):
        str_value = FeatureSetting.get_value_by_name(organization_id=self.organization.id, name=name)
        if str_value is not None and str_value.lower() == "true":
            return True
        else:
            return False;

def get_featuresettingmanager(request):
    return FeatureSettingManager(request)