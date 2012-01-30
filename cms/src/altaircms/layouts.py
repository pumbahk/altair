# coding: utf-8
from pyramid.renderers import get_renderer
from pyramid.decorator import reify

class Layouts(object):
    @reify
    def global_template(self):
        renderer = get_renderer("layout.mako")
        return renderer.implementation().macros['layout']
