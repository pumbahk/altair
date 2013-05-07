# -*- coding:utf-8 -*-

def includeme(config):
    """
    e.g. 
    altaircms.widget.each_organization.settings =
       altaircms.plugins.widget:ticketstar.widget.settings.ini
       altaircms.plugins.widget:89ers.widget.settings.ini
    """
    config.add_directive("add_widgetname", ".helpers.add_widgetname")

    config.include(".widget", route_prefix="api")
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
    config.include(".widget.twitter", route_prefix="api")
    config.include(".widget.rawhtml", route_prefix="api")
    config.include(".jsapi", route_prefix="api")

    ## settings
    from .api import get_configparsers_from_inifiles
    from .api import get_configparser_from_inifile
    from .api import set_widget_aggregator_dispatcher
    from .api import set_widget_aggregator_default
    from .api import set_extra_resource
    from .api import set_extra_resource_default
    from .helpers import list_from_setting_value

    ## plugin 毎の設定ファイルの読み込み
    osettings = config.registry.settings["altaircms.widget.each_organization.settings"]
    inifiles = list_from_setting_value(osettings)
    
    inifile_for_default = config.registry.settings["altaircms.widget.organization.setting.default"]
    configparser_for_default = get_configparser_from_inifile(config, inifile_for_default)

    configparsers = get_configparsers_from_inifiles(config, inifiles)
    set_widget_aggregator_dispatcher(config, configparsers)
    set_widget_aggregator_default(config, configparser_for_default)

    for configparser in configparsers:
        set_extra_resource(config, configparser)
    set_extra_resource_default(config,  configparser_for_default)
    config.set_request_property(".api.get_cart_domain", "cart_domain", reify=True)

