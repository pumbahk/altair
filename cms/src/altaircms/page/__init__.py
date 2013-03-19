# -*- coding:utf-8 -*-

import functools

def install_pageset_searcher(config):
    config.include("altaircms.tag.install_page_tagmanager")
    from ..modelmanager.searcher import PublishingModelSearcher
    pageset = config.maybe_dotted(".models.PageSet")
    PublishingModelSearcher.register(config, pageset)

def includeme(config):
    """ 
    altaircms.page.static.directory: static pageのデータが登録されるディレクトリ
    altaircms.page.tmp.directory: zip fileなどtemporaryなファイルが置かれるディレクトリ
    """
    add_route = functools.partial(config.add_route, factory="altaircms.page.resources.PageResource")
    add_route('page_edit_', '/page/{page_id}/edit')
    add_route("page_detail", "/page/{page_id}")

    add_route('page_add', '/event/{event_id}/page/create/{action}')
    add_route("page_add_orphan", "/page/create/{action}")

    add_route('page_edit', '/event/{event_id}/page/{page_id}/edit')
    add_route("page_delete", "/page/{id}/delete")
    add_route("page_update", "/page/{id}/update")
    add_route("page_duplicate", "/page/{id}/duplicate")
    add_route("page_partial_update", "/page/{id}/partial/{part}")
    add_route('page', '/page/')

    ## widget disposition
    config.add_route("disposition", "/page/{id}/disposition/action/{action}", factory="altaircms.page.resources.WDispositionResource")    
    config.add_route("disposition_list", "/disposition", factory="altaircms.page.resources.WDispositionResource")
    config.add_route("disposition_alter", "/disposition/{id}/alter", factory="altaircms.page.resources.WDispositionResource")

    # PageSet
    # add_route('pageset_list', '/page/{kind}/list')
    add_route("pageset_list", "/page/pagetype/{pagetype}/list")
    config.add_route('pagesets', '/pagesets')
    config.add_route('pageset', '/pagesets/{pageset_id}')
    add_route("pageset_detail", "/pagesets/{pageset_id}/detail/{kind}")
    add_route('pageset_delete', '/pagesets/{pageset_id}/delete')
    config.add_route('pageset_update_term', '/pagesets/{pageset_id}/update_term')

    ## bind event
    config.add_subscriber(".subscribers.page_register_solr", ".subscribers.PageCreate")
    config.add_subscriber(".subscribers.page_register_solr", ".subscribers.PageUpdate")
    config.add_subscriber(".subscribers.page_delete_solr", ".subscribers.PageDelete") ## fixme
    config.add_subscriber("..slackoff.subscribers.update_page_genretag", ".subscribers.PageCreate")

    config.include(install_pageset_searcher)

    from .api import set_static_page_utility
    config.add_route("static_page", "/page/static/{static_page_id}/{action}",factory=".resources.StaticPageResource") 
    config.add_route("static_page_create", "/page/static/{action}",factory=".resources.StaticPageResource") 
    config.add_route("static_page_display", "/page/static/display/{path:.*}",factory=".resources.StaticPageResource")
    settings = config.registry.settings
    set_static_page_utility(
        config, 
        settings["altaircms.page.static.directory"], 
        settings["altaircms.page.tmp.directory"]
        )

    config.scan('.views')
