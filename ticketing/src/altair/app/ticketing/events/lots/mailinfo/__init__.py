def includeme(config):
    config.add_route("tickets.event.lots.mailinfo.preview", "preview/entry/{entry_id}/mailtype/{mailtype}")
    config.add_route("tickets.event.lots.mailinfo.send", "send/entry/{entry_id}/mailtype/{mailtype}")
    config.scan(".views")
