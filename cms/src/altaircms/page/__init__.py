# -*- coding:utf-8 -*-

import functools
def includeme(config):
    """ 
    altaircms.page.static.directory: static pageのデータが登録されるディレクトリ
    altaircms.page.tmp.directory: zip fileなどtemporaryなファイルが置かれるディレクトリ
    """
    settings = config.registry.settings
    config.maybe_dotted(".api.set_static_page_utility")(
        config, 
        settings["altaircms.page.static.directory"], 
        settings["altaircms.page.tmp.directory"]
        )

    add_route = functools.partial(config.add_route, factory="altaircms.page.resources.PageResource")
    add_route('page_edit_', '/page/{page_id}/edit')
    add_route("page_detail", "/page/{page_id}")

    add_route('page_add', '/event/{event_id}/page/create/{action}')
    add_route("page_add_orphan", "/page/create/{action}")

    add_route('page_edit', '/event/{event_id}/page/{page_id}/edit')
    add_route("page_delete", "/page/{id}/delete")
    add_route("page_update", "/page/{id}/update")
    add_route("page_duplicate", "/page/{id}/duplicate")
    
    add_route('page', '/page/')
    add_route('pageset_list', '/page/{kind}/list')

    ## widget disposition
    config.add_route("disposition", "/page/{id}/disposition", factory="altaircms.page.resources.WDispositionResource")    
    ## todo: move bellow
    config.add_route("disposition_list", "/disposition", factory="altaircms.page.resources.WDispositionResource")
    config.add_route("disposition_alter", "/disposition/{id}/alter", factory="altaircms.page.resources.WDispositionResource")

    # PageSet
    config.add_route('pagesets', '/pagesets')
    config.add_route('pageset', '/pagesets/{pageset_id}')
    add_route("pageset_detail", "/pagesets/{pageset_id}/detail/{kind}")
    config.add_route('pageset_delete', '/pagesets/{pageset_id}/delete')
    config.add_route('pageset_update', '/pagesets/{pageset_id}/update')

    ## Static page
    config.add_route("static_page", "/page/static/{static_page_id}/{action}", 
                     factory=".resources.StaticPageResource")
    config.add_route("static_page_create", "/page/static/{action}", 
                     factory=".resources.StaticPageResource")

    ## bind event
    config.add_subscriber(".subscribers.page_register_solr", ".subscribers.PageCreate")
    config.add_subscriber(".subscribers.page_register_solr", ".subscribers.PageUpdate")
    config.add_subscriber(".subscribers.page_delete_solr", ".subscribers.PageDelete") ## fixme

    config.scan('.views')
