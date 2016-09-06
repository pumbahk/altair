def includeme(config):
    from altairsite.separation import enable_smartphone, enable_mobile
    config.add_route("usersite.inquiry", "/inquiry")
    config.add_route("locale", "/locale")
    #mobile
    config.add_view("altairsite.mobile.dispatch.views.dispatch_view", 
                    route_name="usersite.inquiry", 
                    custom_predicates=(enable_mobile, ), 
                    request_type="altair.mobile.interfaces.IMobileRequest")
    config.add_view("altairsite.smartphone.dispatch.views.dispatch_view", 
                    route_name="usersite.inquiry", 
                    custom_predicates=(enable_smartphone, ), 
                    request_type="altair.mobile.interfaces.ISmartphoneRequest")
    config.scan()

