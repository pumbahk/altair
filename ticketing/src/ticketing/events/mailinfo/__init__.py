def includeme(config):
    config.add_route("events.mailinfo.index", "/event/{event_id}")
    config.add_route("events.mailinfo.edit", "/event/{event_id}/mailtype/{mailtype}")
    config.scan(".views")
