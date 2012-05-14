import unittest
from ..genpage import template_to_render
from ..genpage import WidgetNode
from ..genpage import GeneratePageException
from ..genpage import get_pagerender_tree

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
        config = {"widget.template_path_format": "widget/%s.mako"}
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
            blocks = {ABlock.name: ABlock.widgets, 
                      BBlock.name: BBlock.widgets}
        return HasManyBlockPage

    def _get_render(self, fmt):
        from mako.template import Template
        return template_to_render(Template(fmt))

    def test_structure(self):
        page = self._get_page_with_many_blocks()
        page_node = get_pagerender_tree(page)
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
            blocks = {Block.name: Block.widgets}
        return Page

    def test_template(self):
        page = self._get_page()
        page_node = get_pagerender_tree(page)
        render = self._get_render("""content:${widget.content}""")
        self.assertEquals(page_node.concrete(render=render), 
                           {'block': [u'content:a', u'content:b']})

    def test_extra_context(self):
        page = self._get_page()
        page_node = get_pagerender_tree(page)
        render = self._get_render("""${me}:${widget.content}""")
        result = page_node.concrete(render=render, extra_context={"me":"foo"})
        self.assertEquals(result, {'block': [u'foo:a', u'foo:b']})

if __name__ == "__main__":
    unittest.main()
