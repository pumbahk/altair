def includeme(config):
    config.add_route("features", "/features/{path:.*}")
    #mobile
    config.add_view("altairsite.mobile.dispatch.views.dispatch_view", 
                    route_name="features", 
                    request_type="altairsite.mobile.tweens.IMobileRequest")
    config.scan(".views")
