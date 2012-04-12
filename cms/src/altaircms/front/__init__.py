# coding: utf-8

def includeme(config):
    from .resources import  PageRenderingResource
    config.add_route('front', '/publish/{page_name:.*}', factory=PageRenderingResource) # fix-url after. implemnt preview
    config.add_route("front_to_preview", "/to/preview/{page_id}", factory=PageRenderingResource)
    config.add_route('front_preview', '/preview/{page_name:.*}', factory=PageRenderingResource)

    config.scan('.views')
