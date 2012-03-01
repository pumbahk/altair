# -*- encoding:utf-8 -*-
"""
page rendering process: page => widget tree => block_dict(defaultdict(list)) => html
"""
from collections import defaultdict
# from altaircms.structures import uniq_struct

class StoreableMixin(object):
    """ 各widget毎の格納領域を作成するmixin
    """
    def create_store(self, widget, v):
        setattr(self, widget.__class__.__name__, v)
        
    def has_store(self, widget):
        return hasattr(self, widget.__class__.__name__)
    
    def get_store(self, widget):
        return  getattr(self, widget.__class__.__name__)
    

class BlockContext(StoreableMixin):
    """ ページをレンダリングするときに利用する設定。self.blocksが実際にレンダリングされる時に使われる予定。
        ブロック中の各widgetがhtmlを生成するとき、このクラスのインスタンスが設定として渡される。
    　　`blocks'以外の名前のattributeは自由に定義して使って良い。
    """
    DEFAULT_KEYWORDS = ["js_prerender", "js_postrender",
                        "css_prerender", "css_postrender",
                        "title", "description"]
    def __init__(self):
        self._widget_classes = set()
        self.blocks = defaultdict(set)
        for k in self.DEFAULT_KEYWORDS:
            self.blocks[k] = set() #default settings
        
    def __repr__(self):
        fmt = "%s:blocks=%s"
        return fmt % (super(BlockContext, self).__repr__(), 
                      repr(self.blocks))

    def merge(self, D):
        for k, v in D.iteritems():
            self.blocks[k].add(v)

    def add(self, k, v):
        self.blocks[k].add(v)

    def is_attached(self, widget, k):
        return (widget.__class__, k) in self._widget_classes

    def attach_widget(self, widget, k):
        self._widget_classes.add((widget.__class__, k))

    # def add_uniq_widget_class(self, widget, k, v):
    #     if self.is_attached(widget, k):
    #         self.add(k, v)
    #         self.attach_widget(widget, k)

    def scan(self):
        for k, vs in self.blocks.iteritems():
            self.blocks[k] = [v() if callable(v) else v for v in vs]
        return self

    @classmethod
    def from_widget_tree(cls, wtree, scan=True):
        bsettings = cls()
        for bname, widgets in wtree.blocks.iteritems():
            for w in widgets:
                w.merge_settings(bname, bsettings) ## todo: rename method
        bsettings.scan()
        return bsettings

    

