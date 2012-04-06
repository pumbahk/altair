# -*- coding:utf-8 -*-

from js.jquery import jquery
from js.underscore import underscore
from js.jquery_tools import jquery_tools
from js.json2 import json2
# from js.jqueryui import black_tie
from js.jqueryui import smoothness
from js.jqueryui import jqueryui
from js.tinymce import tinymce
from js.backbone import backbone
from js.bootstrap import bootstrap

def bootstrap_need():
    bootstrap.need()

class FanstaticDecoratorFactory(object):
    """ jsを追加するデコレータを作成するファクトリー
    """

    def __init__(self, *fns):
        self.fns = fns
    
    def add(self, fn):
        new = FanstaticDecoratorFactory()
        new.fns = list(self.fns[:])
        new.fns.append(fn)
        return new

    def merge(self, other):
        new = FanstaticDecoratorFactory()
        new.fns = list(self.fns[:])
        new.fns.extend(other.fns[:])
        return new

    ## @todo: support venusian
    def attach(self, wrapped):
        def wraps(context, request, *args, **kwargs):
            response = wrapped(context, request, *args, **kwargs)
            for fn in self.fns:
                if hasattr(fn, "need"):
                    fn.need()
                else:
                    fn()
            return response
        return wraps

    __call__ = attach

"""
how to use decolator

@with_fanstatic_jqueries
@view_config(...)
def view_function(request):
    pass
"""

with_jquery = FanstaticDecoratorFactory(
    jquery.need
)

with_fanstatic_jqueries = FanstaticDecoratorFactory(
    jquery.need,
    jquery_tools.need,
    json2.need,
    jqueryui.need,
    # black_tie.need,
    smoothness.need, 
    underscore.need,
    backbone.need,
    bootstrap.need
)

with_wysiwyg_editor = FanstaticDecoratorFactory(
    tinymce.need
)
with_bootstrap = FanstaticDecoratorFactory(
    bootstrap.need
 )
