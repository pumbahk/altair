# -*- coding:utf-8 -*-

from js.jquery import jquery
from js.underscore import underscore
from js.jquery_tools import jquery_tools
from js.json2 import json2
from js.jqueryui import black_tie
from js.jqueryui import jqueryui
from js.tinymce import tinymce
from js.backbone import backbone
from js.bootstrap import bootstrap
                
import venusian

class FanstaticDecoratorFactory(object):
    """ jsを追加するデコレータを作成するファクトリー
    """

    def __init__(self, *fns):
        self.fns = fns
    
    def add(self, fn):
        self.fns.append(fn)

    ## @todo: support venusian
    def attach(self, wrapped):
        me = self
        class Wrapper(object):
            def __init__(self, wrapped):
                self.callback = wrapped

            def on_scan(self, scanner, name, obj):
                def decorated(*args, **kwargs):
                    ## buggy todo fix
                    try:
                        response = wrapped(*args, **kwargs)
                    except Exception as e:
                        response = wrapped(*args[1:], **kwargs)
                    for fn in me.fns:
                        if hasattr(fn, "need"):
                            fn.need()
                        else:
                            fn()
                            return response
                self.callback = decorated

            def __call__(self, *args, **kwargs):
                return self.callback(*args, **kwargs)
        w = Wrapper(wrapped)
        w.__name__ = wrapped.__name__
        venusian.attach(w, w.on_scan)
        return w

    __call__ = attach

"""
how to use decolator

@with_fanstatic_jqueries
@view_config(...)
def view_function(request):
    pass
"""

with_fanstatic_jqueries = FanstaticDecoratorFactory(
    jquery.need,
    jquery_tools.need,
    json2.need,
    jqueryui.need,
    black_tie.need,
    underscore.need,
    backbone.need
    )

with_wysiwyg_editor = FanstaticDecoratorFactory(
    tinymce.need
)
with_bootstrap = FanstaticDecoratorFactory(
    bootstrap.need
)
