# -*- coding:utf-8 -*-

from altaircms.interfaces import IConcreteNode
from zope.interface import implements
from pyramid.renderers import render as default_render
from collections import defaultdict

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

# layout?
class PageNode(object):
    implements(IConcreteNode)

    def __init__(self):
        self.blocks = {}
        self.result = {}

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
    WIDGET_FILE = "widget_file_format"

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
        if hasattr(self.widget, "template_name"):
            return self.widget.template_name
        elif self.config and self.WIDGET_FILE in self.config:
            fmt = self.config[self.WIDGET_FILE]
            return fmt % self.widget.type
        else:
            raise GeneratePageException("widget template file is not found")

    def concrete(self, request=None, config=None, extra_context=None, render=None):
        ## pyramid.renderers.render() 's _request' argument is optional.
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

def get_page_node_from_page(page):
    root = PageNode()
    for block in page.blocks:
        bname = block.name
        for w in block.widgets:
            root.add(bname, w)
    return root

if __name__ == "__main__":
    import unittest
    class WidgetNodeTest(unittest.TestCase):
        def test_it(self):
            from mako.template import Template
            render = template_to_render(Template("foo"))
            WidgetNode("widget", "template.mak", render=render).concrete()

        def test_adapt_it(self):
            from mako.template import Template
            render = template_to_render(Template("""${foo}"""))
            wn = WidgetNode("widget", "template.mak", render=render)
            wn.concrete(extra_context={"foo": "foobar"})

        def test_find_template_false_if_not_config(self):
            class widget(object):
                type = "image"
            wn = WidgetNode(widget)
            self.assertRaises(GeneratePageException,  lambda : wn.template)

        def test_find_template_from_widget_type_and_config(self):
            config = {"widget_file_format": "widget/%s.mako"}
            class widget(object):
                type = "image"
            wn = WidgetNode(widget)
            wn.configure(config)
            self.assertEquals("widget/image.mako", wn.template)

        def test_find_template_from_widget(self):
            class widget(object):
                template_name = "image/foo.mako"
            wn = WidgetNode(widget)
            self.assertEquals("image/foo.mako", wn.template)
            
    class GetPageNodeTest(unittest.TestCase):
        def _get_page_with_many_blocks(self):
            class Widget(object):
                template_name = "dummy"
                def __init__(self, n):
                    self.n = n
            class ABlock(object):
                name = "A"
                widgets = [Widget(i) for i in [1, 2, 3]]
            class BBlock(object):
                name = "B"
                widgets = [Widget(i) for i in [4, 5]]
            class HasManyBlockPage(object):
                blocks = [ABlock, BBlock]
            return HasManyBlockPage

        def _get_render(self, fmt):
            from mako.template import Template
            return template_to_render(Template(fmt))
            
        def test_structure(self):
            page = self._get_page_with_many_blocks()
            page_node = get_page_node_from_page(page)
            render = self._get_render("""${widget.n}""")
            self.assertEquals(page_node.concrete(render=render), 
                              {'A': ["1", "2", "3"], 'B': ["4", "5"]})

        def _get_page(self):
            class Widget(object):
                def __init__(self, content):
                    self.content = content
                template_name = "foo.mako"
            class Block(object):
                name = "block"
                widgets = [Widget("a"), Widget("b")]
            class Page(object):
                blocks = [Block]
            return Page

        def test_template(self):
            page = self._get_page()
            page_node = get_page_node_from_page(page)
            render = self._get_render("""content:${widget.content}""")
            self.assertEquals(page_node.concrete(render=render), 
                               {'block': [u'content:a', u'content:b']})

        def test_extra_context(self):
            page = self._get_page()
            page_node = get_page_node_from_page(page)
            render = self._get_render("""${me}:${widget.content}""")
            result = page_node.concrete(render=render, extra_context={"me":"foo"})
            self.assertEquals(result, {'block': [u'foo:a', u'foo:b']})

    unittest.main()
