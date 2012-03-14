def includeme(config):
    # config.add_route('page_list', '/page/', factory="altaircms.page.resources.PageResource")
    config.add_route('page_edit_', '/page/{page_id}', factory="altaircms.page.resources.PageResource")

    config.add_route('page_add', '/event/{event_id}/page/')
    config.add_route('page_edit', '/event/{event_id}/page/{page_id}/edit', factory="altaircms.page.resources.PageResource")
    config.add_route("page_delete", "/page/{id}/delete")
    config.add_route("page_update", "/page/{id}/update")
    config.add_route("page_update_confirm", "/page/{id}/update/confirm")
    config.add_route("page_settings", "/page/{id}/settings")
    config.add_route('page', '/page/')
    # config.add_route('page_object', '/page/{id}')
