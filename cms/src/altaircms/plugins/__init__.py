# -*- coding:utf-8 -*-

def includeme(config):
    """
    e.g. 
    altaircms.widget.each_organization.settings =
       altaircms.plugins.widget:ticketstar.widget.settings.ini
       altaircms.plugins.widget:89ers.widget.settings.ini
    altaircms.stage = "stating" ## candidates = ["production", "dev", "staging", "local"]
    """
    config.add_directive("add_widgetname", ".helpers.add_widgetname")

    config.include(".extra")
    config.include(".widget.image", route_prefix="api")
    config.include(".widget.freetext", route_prefix="api")
    config.include(".widget.flash", route_prefix="api")
    config.include(".widget.movie", route_prefix="api")
    config.include(".widget.calendar", route_prefix="api")
    config.include(".widget.performancelist", route_prefix="api")
    # config.include(".widget.detail", route_prefix="api")
    config.include(".widget.ticketlist", route_prefix="api")
    config.include(".widget.menu", route_prefix="api")
    config.include(".widget.topic", route_prefix="api")
    config.include(".widget.topcontent", route_prefix="api")
    config.include(".widget.breadcrumbs", route_prefix="api")
    config.include(".widget.summary", route_prefix="api")
    config.include(".widget.countdown", route_prefix="api")
    # config.include(".widget.reuse", route_prefix="api")
    config.include(".widget.iconset", route_prefix="api")
    config.include(".widget.linklist", route_prefix="api")
    config.include(".widget.heading", route_prefix="api")
    config.include(".widget.promotion", route_prefix="api")
    config.include(".widget.anchorlist", route_prefix="api")
    config.include(".widget.purchase", route_prefix="api")
    config.include(".widget.lotsreview", route_prefix="api")
    config.include(".widget.twitter", route_prefix="api")
    config.include(".widget.rawhtml", route_prefix="api")
    config.include(".jsapi", route_prefix="api")

    config.include(install_extra_config_features)

## todo:rename
def install_extra_config_features(config):
    ## settings
    from .config import ConfigParserBuilder
    from .config import WidgetSettingsSetup
    from .helpers import list_from_setting_value

    ## plugin 毎の設定ファイルの読み込み
    settings = config.registry.settings
    
    cfgparse_builder = ConfigParserBuilder(config)
    configparser_for_default = cfgparse_builder.from_inifile(settings["altaircms.widget.organization.setting.default"])
    configparsers = cfgparse_builder.list_from_inifile_list(
        list_from_setting_value(
            settings["altaircms.widget.each_organization.settings"]))

    setup = WidgetSettingsSetup(config, settings["altaircms.stage"])
    setup.each_settings(configparsers)
    setup.default_setting(configparser_for_default)
