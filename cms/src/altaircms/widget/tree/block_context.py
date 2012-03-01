# -*- encoding:utf-8 -*-
"""
page rendering process: page => widget tree => block_dict(defaultdict(list)) => html
"""

from altaircms.structures import uniq_struct
class BlockContext(object):
    """ ページをレンダリングするときに利用する設定。self.blocksが実際にレンダリングされる時に使われる予定。
        ブロック中の各widgetがhtmlを生成するとき、このクラスのインスタンスが設定として渡される。
    　　`blocks'以外の名前のattributeは自由に定義して使って良い。

    >>> bsettings =  BlockContext()

    >>> bsettings.add("foo", 1)
    >>> bsettings.blocks
    {'description': set([]), 'js_prerender': set([]), 'title': set([]), 'js_postrender': set([]), 'foo': set([1]), 'css_postrender': set([]), 'css_prerender': set([])}

    >>> bsettings.merge({"bar": 2})
    >>> bsettings.blocks
    {'bar': set([2]), 'description': set([]), 'js_prerender': set([]), 'title': set([]), 'js_postrender': set([]), 'foo': set([1]), 'css_postrender': set([]), 'css_prerender': set([])}
    """
    DEFAULT_KEYWORDS = ["js_prerender", "js_postrender",
                        "css_prerender", "css_postrender",
                        "title", "description"]
    def __init__(self):
        self.blocks = uniq_struct(default_keywords=self.DEFAULT_KEYWORDS)
        
    def __repr__(self):
        fmt = "%s:blocks=%s"
        return fmt % (super(BlockContext, self).__repr__(), 
                      repr(self.blocks))

    def merge(self, D):
        for k, v in D.iteritems():
            self.blocks[k] = v

    def add(self, k, v):
        self.blocks[k] = v

    @classmethod
    def from_widget_tree(cls, wtree):
        bsettings = cls()
        for bname, widgets in wtree.blocks.items():
            for w in widgets:
                w.merge_settings(bsettings) ## todo: rename method
        return bsettings

if __name__ == "__main__":
    import doctest
    doctest.testmod()
