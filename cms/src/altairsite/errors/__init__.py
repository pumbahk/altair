# coding: utf-8

def includeme(config):
    notfound_template = config.registry.settings["altaircms.usrsite.notfound.template"]
    forbidden_template = config.registry.settings["altaircms.usrsite.forbidden.template"]

    config.add_view(".views.notfound", context="pyramid.exceptions.NotFound", renderer=notfound_template)
    config.add_view(".views.forbidden", context="pyramid.exceptions.Forbidden", renderer=forbidden_template)
