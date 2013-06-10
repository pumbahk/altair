def includeme(config):
    config.add_route("usersite.order", "/order")
    #mobile
    config.add_view("altairsite.mobile.dispatch.views.dispatch_view", 
                    route_name="usersite.order", 
                    request_type="altairsite.tweens.IMobileRequest")
    config.add_view("altairsite.smartphone.dispatch.views.dispatch_view", 
                    route_name="usersite.order", 
                    request_type="altairsite.tweens.ISmartphoneRequest")
    config.scan()
