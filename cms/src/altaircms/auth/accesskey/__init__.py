#
def includeme(config):
    ## access key
    config.add_route("external.auth.accesskey.info", "/api/accesskey/info")
    config.add_route("auth.accesskey.pagekey", "/api/page/{page_id}/accesskey/{action}")
    config.add_route("auth.accesskey.eventkey", "/api/event/{event_id}/accesskey/{action}")
    config.add_route("auth.accesskey.detail", "/accesskey/{accesskey_id}")
    config.scan(".views")  
