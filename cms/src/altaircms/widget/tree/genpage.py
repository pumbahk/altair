# -*- coding:utf-8 -*-

from altaircms.interfaces import IConcreteNode
from altaircms.interfaces import IBlockTree
from zope.interface import implements
from pyramid.renderers import render as default_render
from collections import defaultdict
import os.path

WIDGET_TEMPLATE_PATH_FORMAT = "widget.template_path_format"
WIDGET_LAYOUT_DIRECTORIES = "widget.layout_directories"

class GeneratePageException(Exception):
    pass

"""
page > block > widget
e.g.

<page>
   <block>
     a widget
     b widget
     c widget
   </block>
</page>


for block in page.blocks:
   bname = block.name
   for widget in blocks.widgets:
       yield widget
"""

class PageNode(object):
    implements(IConcreteNode, IBlockTree)

    def __init__(self):
        self.blocks = {}
        self.result = defaultdict(list)

    def add(self, block_name, widget):
        if not block_name in self.blocks:
            self.blocks[block_name] = BlockNode(block_name)
        self.blocks[block_name].add(widget)

    def clear(self):
        if self.result:
            for b in self.result.values():
                b.clear()

    def concrete(self, request=None, config=None, extra_context=None, render=None):
        if self.result:
            return self.result
        extra_context = extra_context or {}
        for bn, block in self.blocks.items():
            self.result[bn] = block.concrete(request=request, 
                                             config=config,
                                             extra_context=extra_context, 
                                             render=render)
        return self.result
    
class BlockNode(object):
    implements(IConcreteNode)

    def __init__(self, block_name):
        self.block_name = block_name
        self.widgets = []
        self.results = []

    def add(self, widget):
        self.widgets.append(WidgetNode(widget))

    def clear(self):
        self.results = []

    def concrete(self, request=None, config=None, extra_context=None, render=None):
        if self.results:
            return self.results
        for w in self.widgets:
            html = w.concrete(request=request, 
                              config=config,
                              extra_context=extra_context, 
                              render=render)
            self.results.append(html)
        return self.results

class WidgetNode(object):
    """
    + find_template is 3way
       + constructor argument(template)
       + widget.template_name
       + config: {"widget_fyle_format"} + widget.type

    how to use:
    WidgetNode(widget).render(request, {"foo":bar})
    """

    implements(IConcreteNode)

    def __init__(self, widget,template=None, render=default_render):
        self.widget = widget
        self._template = template
        self.render = render
        self.config = {}

    @property
    def template(self):
        if self._template:
            return self._template
        v = self._find_template()
        self._template = v
        return v

    def configure(self, config):
        self.config.update(config)

    def _find_template(self):
        if self.config and WIDGET_TEMPLATE_PATH_FORMAT in self.config:
            fmt = self.config[WIDGET_TEMPLATE_PATH_FORMAT]
            return fmt % self.widget.type
        elif hasattr(self.widget, "template_name"):
            return self.widget.template_name
        else:
            raise GeneratePageException("widget template file is not found")

    def concrete(self, request=None, config=None, extra_context=None, render=None):
        ## pyramid.renderers.render() 's `request' argument is optional.
        ## so, request=None is ok.
        if config:
            self.configure(config)
        ctx = {"widget": self.widget}

        if extra_context:
            ctx.update(extra_context)

        if render:
            return render(self.template, ctx, request=request)
        else:
            return self.render(self.template, ctx, request=request)

class RenderAdaptor(object):
    """swapping render() in pyramid.renderer to simple template function,  for testing."""

    def __init__(self, template):
        self.template = template

    def _add_context(self, D, kwargs):
        r = D.copy()
        r.update(kwargs)
        return r

    def render(self, renderer_name, value, request=None, package=None):
        params =  dict(__renderer_name=renderer_name, 
                       __request=request, 
                       __package=package)
        return self.template.render(**self._add_context(value,params))

## main
def template_to_render(template):
    return RenderAdaptor(template).render

def get_config(request):
    config = {}
    settings = request.registry.settings
    template_format = settings.get(WIDGET_TEMPLATE_PATH_FORMAT)
    if template_format:
        config[WIDGET_TEMPLATE_PATH_FORMAT] = template_format
    layout_dir = settings.get(WIDGET_LAYOUT_DIRECTORIES)
    if layout_dir:
        config[WIDGET_LAYOUT_DIRECTORIES] = layout_dir
    return config

def get_layout_template(template_filename, config):
    return os.path.join(config[WIDGET_LAYOUT_DIRECTORIES], template_filename)

def get_pagerender_tree(widget_tree):
    root = PageNode()
    for bname, widgets in widget_tree.blocks.items():
        for w in widgets:
            root.add(bname, w)
    return root
