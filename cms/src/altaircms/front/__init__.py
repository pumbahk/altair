# coding: utf-8

def includeme(config):
    from .resources import  PageRenderingResource
    config.add_route('front', '/{page_name:.*}', factory=PageRenderingResource)
