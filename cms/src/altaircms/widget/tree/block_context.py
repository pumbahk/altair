# -*- encoding:utf-8 -*-
"""
page rendering process: page => widget tree => block_dict(defaultdict(list)) => html
"""
from collections import defaultdict
from altaircms.lib.structures import StrictDict

__all__ = ["BlockContextException",
           "BlockContext"]

class BlockContextException(Exception):
    pass

class StoreableMixin(object):
    """ 各widget毎の格納領域を作成するmixin
    """
    def create_store(self, widget, v):
        setattr(self, widget.__class__.__name__, v)
        
    def has_store(self, widget):
        return hasattr(self, widget.__class__.__name__)
    
    def get_store(self, widget):
        return  getattr(self, widget.__class__.__name__)
    

class UpdatableMixin(object):
    """ データを更新するmixin
        self.blocksを更新する
    """
    def merge(self, D):
        for k, v in D.iteritems():
            self.blocks[k].append(v)

    def add(self, k, v):
        self.blocks[k].append(v)

class UniqueByWidgetMixin(object):
    """ widget毎に設定を一度きりのみ設定できるようにするmixin
        値をself._widget_classに格納する
    """
    def is_attached(self, widget, k):
        return (widget.__class__, k) in self._widget_classes

    def attach_widget(self, widget, k):
        self._widget_classes.add((widget.__class__, k))

class ScannableMixin(object):
    """ scanフェイズの実行を行うmixin
        scanフェイズでは以下の処理を行う
        1. 外部コンテキスト情報の注入
        2. 関数化していたレンダリング内容を文字列(html)に変換
    """
    category_candidates = ("before_scan", "after_scan")
    def _collect_validators(self, category=None):
        if category is None:
            return (vald for _,  vald in self._validators)
        else:
            return (vald for c, vald in self._validators if c == category)

    def _do_validate(self, category=None):
        valds = self._collect_validators(category)
        for v in valds:
            if not v(self):
                raise BlockContextException(v.__doc__)

    def attach_validator(self, fn, category=None):
        if category and not category in self.category_candidates:
            raise BlockContextException("%s is not found in category_candidates" % category)
        self._validators.append((category, fn))

    def scan(self, **kwargs):
        self.is_scaned = True
        self.extra.update(kwargs)
        self._do_validate("before_scan")
        for k, vs in self.blocks.iteritems():
            self.blocks[k] = [v() if callable(v) else v for v in vs]
        self._do_validate("after_scan")    

class BlockContext(StoreableMixin,
                   UpdatableMixin,
                   ScannableMixin, 
                   UniqueByWidgetMixin):
    """ ページをレンダリングするときに利用する設定。self.blocksが実際にレンダリングされる時に使われる予定。
        ブロック中の各widgetがhtmlを生成するとき、このクラスのインスタンスが設定として渡される。
        blocks, is_scanned, extra以外の名前のattributeを自由に定義して使って良い。
    """
    DEFAULT_KEYWORDS = ["js_prerender", "js_postrender",
                        "css_prerender", "css_postrender",
                        "title", "description"]
    def __init__(self, extra=None):
        self._widget_classes = set()
        self.blocks = defaultdict(list)
        for k in self.DEFAULT_KEYWORDS:
            self.blocks[k] = list() #default list

        self.is_scaned = False
        self._validators = list()
        self.extra = StrictDict()
        if extra:
            self.extra.update(extra)

    def need_extra_in_scan(self, valname):
        def has_val(settings):
            # return settings.extra.get(valname, None) is not None
            return valname in settings.extra
        has_val.__doc__ = "self.extra['%s'] is not found" % valname
        self.attach_validator(has_val, category="before_scan")        

    def __repr__(self):
        fmt = "%s:blocks=%s"
        return fmt % (super(BlockContext, self).__repr__(), 
                      repr(self.blocks))

    @classmethod
    def from_widget_tree(cls, wtree, scan=True):
        bsettings = cls()
        for bname, widgets in wtree.blocks.iteritems():
            for w in widgets:
                w.merge_settings(bname, bsettings) ## todo: rename method
        return bsettings

    

