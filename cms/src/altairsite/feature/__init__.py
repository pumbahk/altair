def includeme(config):
    config.add_route("features", "/features/{path:.*}")
    #mobile
    config.add_view("altairsite.mobile.dispatch.views.dispatch_view", 
                    route_name="features", 
                    request_type="altairsite.tweens.IMobileRequest")
    config.add_view("altairsite.smartphone.dispatch.views.dispatch_view", 
                    route_name="features", 
                    request_type="altairsite.tweens.ISmartphoneRequest")
    config.scan(".views")
