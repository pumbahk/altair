# coding: utf-8

def includeme(config):

    config.add_route('front', '/publish/{page_name:.*}', factory=".resources.PageRenderingResource") # fix-url after. implemnt preview
    config.add_route("front_to_preview", "/to/preview/{page_id}", factory=".resources.PageRenderingResource")
    config.add_route('front_preview', '/{page_id}/preview/{page_name:.*}', factory=".resources.PageRenderingResource")

    config.scan('.views')
