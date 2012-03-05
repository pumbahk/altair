# -*- coding:utf-8 -*-

class DummyWidget(object):
    def __init__(self, name):
        self.name = name

    def to_html(self):
        return "<p>%s</p>" % self.name

    def merge_settings(self, bname, bcontext):
        D = {bname: self.to_html()}
        bcontext.merge(D)

class NeedValueWidget(DummyWidget):
    def merge_settings(self, bname, bcontext):
        bcontext.need_extra_in_scan("user")
        def top_html():
            user = bcontext.extra["user"]
            return "<p>user: %s</p>" % user
        bcontext.merge({"top": top_html})

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

    def _attach_jscode_if_need(self, bcontext):
        if not bcontext.is_attached(self, "js_prerender"):
            def to_html():
                code = """function echo(i){console.log(i)} 
                _.each([%s], echo);
                """ % ", ".join(bcontext.get_store(self))
                return code
            bcontext.add("js_prerender", to_html)
            bcontext.attach_widget(self, "js_prerender")
        
    def merge_settings(self, bname, bcontext):
        self._attach_jscode_if_need(bcontext)
        bcontext.add(bname, self.to_html())

        if not bcontext.has_store(self):
            bcontext.create_store(self, [])
        bcontext.get_store(self).append(str(self.id))

import unittest
from altaircms.widget.tree.block_context import BlockContext

class BlockContextTest(unittest.TestCase):
    def test_simple(self):
        """動作チェック
        """
        class WTree(object):
            blocks = {"top": [DummyWidget("foo"), DummyWidget("bar")]}

        bcontext = BlockContext.from_widget_tree(WTree)
        bcontext.scan()
        self.assertEquals("".join(bcontext.blocks["top"]),
                          '<p>bar</p><p>foo</p>')

    def test_with_js_widget(self):
        """関数を含んだwidgetで動作チェック
        """
        class WTree(object):
            blocks = {"top": [WithJSWidget("foo", 1), WithJSWidget("bar", 2)]}
        bcontext = BlockContext.from_widget_tree(WTree)
        bcontext.scan()
        self.assertEquals("".join(bcontext.blocks["top"]),
                          '<p id="1">foo</p><p id="2">bar</p>')

    def test_jscode(self):
        """ 複数のwidgetの内容をマージして、ひとつの部分(jscode)を生成できているか確認
        """
        class WTree(object):
            blocks = {"top": [WithJSWidget("foo", 1), WithJSWidget("bar", 2)]}
        bcontext = BlockContext.from_widget_tree(WTree)
        bcontext.scan()
        self.assertEquals(list(bcontext.blocks["js_prerender"])[0], 
                          """function echo(i){console.log(i)} 
                _.each([1, 2], echo);
                """)

    def test_external_context(self):
        """外部コンテキストの注入のチェック
        """
        class WTree(object):
            blocks = {"top": [DummyWidget("foo")]}
        bcontext = BlockContext.from_widget_tree(WTree)
        bcontext.scan(user="user")
        self.assertEquals(bcontext.extra["user"], "user")

    def test_extra_raise_exception_if_not_found(self):
        """指定した値がself.extraに存在しなかった場合例外が投げられるはず
        """
        class WTree(object):
            blocks = {"top": [NeedValueWidget("foo")]}
        bcontext = BlockContext.from_widget_tree(WTree)

        from altaircms.widget.tree.block_context import BlockContextException
        self.assertRaises(BlockContextException, bcontext.scan)
        
    def test_extra_validator_ok(self):
        """指定した値がself.extraにあった場合はok
        """
        class WTree(object):
            blocks = {"top": [NeedValueWidget("foo")]}
        bcontext = BlockContext.from_widget_tree(WTree)
        bcontext.scan(user="user")
        self.assertEquals(list(bcontext.blocks["top"])[0], 
                          "<p>user: user</p>")
        
        
if __name__ == "__main__":

    unittest.main()
