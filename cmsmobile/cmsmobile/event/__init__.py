# -*- coding: utf-8 -*-

def includeme(config):
    config.add_route('search', '/search', factory="altaircms.topic.resources.TopcontentPageContext")
    config.add_route("genre", "/genre", factory="altaircms.topic.resources.TopcontentPageContext")
    config.add_route('detail', '/detail', factory="altaircms.topic.resources.TopcontentPageContext")
    config.add_route('inquiry', '/inquiry', factory="altaircms.topic.resources.TopcontentPageContext")
    config.add_route('help', '/help', factory="altaircms.topic.resources.TopcontentPageContext")
    config.add_route('order', '/order', factory="altaircms.topic.resources.TopcontentPageContext")
