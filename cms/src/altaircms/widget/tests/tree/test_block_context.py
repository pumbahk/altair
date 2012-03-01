class DummyWidget(object):
    def __init__(self, name):
        self.name = name

    def to_html(self):
        return "<p>%s</p>" % self.name

    def merge_settings(self, bname, bsettings):
        D = {bname: self.to_html()}
        bsettings.merge(D)

class WithJSWidget(object):
    def __init__(self, name, id):
        self.name = name
        self.id = id

    def to_html(self):
        return "<p id=\"%d\">%s</p>" % (self.id, self.name)

    def jscode(self, ids):
        return """
"function echo(i){console.log(i)}
_.each(%s, echo);
""" % ids

    def _attach_jscode_if_need(self, bsettings):
        if not bsettings.is_attached(self, "js_prerender"):
            def to_html():
                code = """function echo(i){console.log(i)} 
                _.each([%s], echo);
                """ % ", ".join(bsettings.js_widget_ids)
                return code
            bsettings.add("js_prerender", to_html)
            bsettings.attach_widget(self, "js_prerender")
        
    def merge_settings(self, bname, bsettings):
        self._attach_jscode_if_need(bsettings)
        bsettings.add(bname, self.to_html())

        if not hasattr(bsettings, "js_widget_ids"):
            bsettings.js_widget_ids = []
        bsettings.js_widget_ids.append(str(self.id))
        

import unittest
from altaircms.widget.tree.block_context import BlockContext

class BlockContextTest(unittest.TestCase):
    def test_simple(self):
        class WTree(object):
            blocks = {"top": [DummyWidget("foo"), DummyWidget("bar")]}

        bsettings = BlockContext.from_widget_tree(WTree)
        self.assertEquals("".join(bsettings.blocks["top"]),
                          '<p>bar</p><p>foo</p>')

    def test_with_js_widget(self):
        class WTree(object):
            blocks = {"top": [WithJSWidget("foo", 1), WithJSWidget("bar", 2)]}
        bsettings = BlockContext.from_widget_tree(WTree)
        self.assertEquals("".join(bsettings.blocks["top"]),
                          '<p id="1">foo</p><p id="2">bar</p>')

    def test_jscode(self):
        class WTree(object):
            blocks = {"top": [WithJSWidget("foo", 1), WithJSWidget("bar", 2)]}
        bsettings = BlockContext.from_widget_tree(WTree)

        self.assertEquals(bsettings.blocks["js_prerender"].pop()(), 
                          """function echo(i){console.log(i)} 
                _.each([1, 2], echo);
                """)
        
if __name__ == "__main__":
    unittest.main()
