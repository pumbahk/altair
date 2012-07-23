from .helpers import list_from_setting_value

def includeme(config):
    """
    e.g. 
    altaircms.widget.each_organization.settings =
       altaircms.plugins.widget:ticketstar.widget.settings.ini
       altaircms.plugins.widget:89ers.widget.settings.ini
    """
    config.add_directive("add_widgetname", ".helpers.add_widgetname")

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

    ## todo: move ini
    inifiles = list_from_setting_value(config.registry.settings["altaircms.widget.each_organization.settings"])
    set_widget_aggregator_dispatcher = config.maybe_dotted(".api.set_widget_aggregator_dispatcher")
    set_widget_aggregator_dispatcher(config, inifiles)

    config.include(".jsapi", route_prefix="api")

