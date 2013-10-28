def includeme(config):
    from altairsite.separation import enable_mobile
    from altairsite.front.cache import with_mobile_cache
    config.add_route("features", "/features/{page_name:.*}")
    #mobile
    config.add_view("altairsite.mobile.staticpage.views.staticpage_view", 
                    route_name="features", 
                    request_type="altairsite.tweens.IMobileRequest", 
                    decorator=with_mobile_cache)
    config.scan(".views")
