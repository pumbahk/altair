# -*- encoding:utf-8 -*-
"""
page rendering process: page => widget tree => block_dict(defaultdict(list)) => html
"""
from collections import defaultdict
import logging
logger = logging.getLogger(__name__)

__all__ = ["BlockSettingsException",
           "BlockSettings"]

class StrictDict(dict):
    """ subspecies. a value of getitem from this is None raise KeyError
    >>> sd = StrictDict(foo="bar")

    >>> sd["v"] = None
    >>> ## key error sd["v"] 

    >>> sd["v"] = 1
    >>> sd["v"]
    1
    """
    def __getitem__(self, k):
        v = super(StrictDict, self).__getitem__(k)
        if v is None:
            raise KeyError(u".%s is not found (strict dict not support getting None value)" % k)
        return v
      

class BlockSettingsException(Exception):
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
    subkind_candidates = ("before_scan", "after_scan")
    def _collect_validators(self, subkind=None):
        if subkind is None:
            return (vald for _,  vald in self._validators)
        else:
            return (vald for c, vald in self._validators if c == subkind)

    def _do_validate(self, subkind=None):
        valds = self._collect_validators(subkind)
        for v in valds:
            if not v(self):
                raise BlockSettingsException(v.__doc__)

    def attach_validator(self, fn, subkind=None):
        if subkind and not subkind in self.subkind_candidates:
            raise BlockSettingsException("%s is not found in subkind_candidates" % subkind)
        self._validators.append((subkind, fn))

    def scan(self, request=None, **kwargs):
        kwargs["request"] = request ##?
        self.is_scaned = True
        self.extra.update(kwargs)
        self._do_validate("before_scan")
        for k, vs in self.blocks.iteritems():
            correct_vals = []
            for v in vs:
                if callable(v):
                    try:
                        v = v()
                    except Exception, e:
                        try:
                            logger.warn("bsettings %s has invalid rendering closure. error=%s, (extra_resource=%s)" % (k, repr(e), self.extra))
                            v = str(e)
                        except UnicodeError:
                            logger.warn("bsettings %s. unicode error" % k)
                            v = "bsettings %s. unicode error" % k
                if v is None:
                    logger.warn("bsettings %s is None. (extra_resource=%s)" % (k, self.extra))
                else:
                    correct_vals.append(v)
            self.blocks[k] = correct_vals
        self._do_validate("after_scan")    

class BlockSettings(StoreableMixin,
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
        self.attach_validator(has_val, subkind="before_scan")        

    def __repr__(self):
        fmt = "%s:blocks=%s"
        return fmt % (super(BlockSettings, self).__repr__(), 
                      repr(self.blocks))

    @classmethod
    def from_widget_tree(cls, wtree):
        bsettings = cls()
        for bname, widgets in wtree.blocks.iteritems():
            for w in widgets:
                w.merge_settings(bname, bsettings) ## todo: rename method
        return bsettings
