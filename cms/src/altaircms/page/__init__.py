def includeme(config):
    # config.add_route('page_list', '/page/', factory="altaircms.page.resources.PageResource")
    config.add_route('page_edit_', '/page/{page_id}', factory="altaircms.page.resources.PageResource")
    config.add_route('page_add', '/event/{event_id}/page/', factory="altaircms.page.resources.PageResource")
    config.add_route('page_edit', '/event/{event_id}/page/{page_id}/edit', factory="altaircms.page.resources.PageResource")
    config.add_route("page_delete", "/page/{id}/delete")
    config.add_route("page_update", "/page/{id}/update", factory="altaircms.page.resources.PageResource")
    config.add_route("page_duplicate", "/page/{id}/duplicate", factory="altaircms.page.resources.PageResource")
    config.add_route('page', '/page/', factory="altaircms.page.resources.PageResource")
    # config.add_route('page_object', '/page/{id}')

    config.add_route("disposition", "/page/{id}/disposition", factory="altaircms.page.resources.PageResource")    
    ## todo: move bellow
    config.add_route("disposition_list", "/disposition", factory="altaircms.page.resources.PageResource")
    config.add_route("disposition_alter", "/disposition/{id}/alter", factory="altaircms.page.resources.PageResource")

    # PageSet
    config.add_route('pagesets', '/pagesets')
    config.add_route('pageset', '/pagesets/{pageset_id}')
    config.add_route('pageset_delete', '/pagesets/{pageset_id}/delete')
    config.add_route('pageset_update', '/pagesets/{pageset_id}/update')

    config.scan('.views')
