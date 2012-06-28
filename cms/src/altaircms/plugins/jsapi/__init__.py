def includeme(config):
    config.add_view(".views.performance_add_getti_code",  permission="performance_update", 
                     route_name="plugins_jsapi_getti", 
                     renderer="json")
    config.add_route("plugins_jsapi_getti", "/plugins/performance/getti")
