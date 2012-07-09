# -*- coding:utf-8 -*-
## todo: urlなど整理
def includeme(config):
    config.add_route("plugins_jsapi_getti", "/plugins/performance/getti")

    ## page
    config.add_route("plugins_jsapi_addpage", "/plugins/pageset/{pageset_id}/addpage")
    config.add_route("plugins_jsapi_page_publish_status", "/plugins/page/publish/{page_id}/{status}")
    config.add_route("plugins_api_page_info_default", "/page/api/setupinfo")
    config.add_route("plugins_jsapi_pageset_reset_event", "/plugins/pageset/{pageset_id}/reset_event")

    ## tag
    config.add_route("plugins_jsapi_page_tag_delete", "/page/api/page/{page_id}/tag/delete")
    config.scan(".views")
    
    ## access key
    config.add_route("plugins_jsapi_accesskey", "/page/api/page/{page_id}/accesskey/{action}")
