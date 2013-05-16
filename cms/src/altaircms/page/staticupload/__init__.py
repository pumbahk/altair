def includeme(config):
    from .api import set_static_page_utility
    config.add_route("static_page", "/page/static/{static_page_id}/{action}",factory=".resources.StaticPageResource") 
    config.add_route("static_page_create", "/page/static/{action}",factory=".resources.StaticPageResource") 
    config.add_route("static_page_display", "/page/static/display/{path:.*}",factory=".resources.StaticPageResource")
    settings = config.registry.settings
    set_static_page_utility(
        config, 
        settings["altaircms.page.static.directory"], 
        settings["altaircms.page.tmp.directory"]
        )
    config.scan(".views")

