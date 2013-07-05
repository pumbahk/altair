def includeme(config):
    from altairsite.separation import enable_smartphone, enable_mobile
    config.add_route("usersite.inquiry", "/inquiry")
    #mobile
    config.add_view("altairsite.mobile.dispatch.views.dispatch_view", 
                    route_name="usersite.inquiry", 
                    custom_predicates=(enable_mobile, ), 
                    request_type="altairsite.tweens.IMobileRequest")
    config.add_view("altairsite.smartphone.dispatch.views.dispatch_view", 
                    route_name="usersite.inquiry", 
                    custom_predicates=(enable_smartphone, ), 
                    request_type="altairsite.tweens.ISmartphoneRequest")
    config.scan()
