def includeme(config):
    config.scan()

    from .helpers import OrganizationSettingRenderer, EventSettingRenderer
    from .models import OrganizationSetting, EventSetting
    from .interfaces import ISettingRenderer
    config.registry.registerAdapter(OrganizationSettingRenderer, (OrganizationSetting,), ISettingRenderer)
    config.registry.registerAdapter(EventSettingRenderer, (EventSetting,), ISettingRenderer)
