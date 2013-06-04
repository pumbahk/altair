def includeme(config):
    config.add_route("usersite.inquiry", "/inquiry")
    #mobile
    config.add_view("altairsite.mobile.dispatch.views.dispatch_view", 
                    route_name="usersite.inquiry", 
                    request_type="altairsite.tweens.IMobileRequest")
    config.scan()
