def includeme(config):
    config.add_route("plugins_jsapi_getti", "/plugins/performance/getti")

    ## page
    config.add_route("plugins_jsapi_addpage", "/plugins/pageset/{pageset_id}/addpage")
    config.add_route("plugins_jsapi_page_publish_status", "/plugins/page/publish/{page_id}/{status}")
    config.add_route("api_page_setup_info", "/page/api/setupinfo")

    config.scan(".views")
