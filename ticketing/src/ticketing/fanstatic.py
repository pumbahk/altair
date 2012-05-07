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
from js.jquery_timepicker_addon import timepicker
from js.jquery_colorpicker import jquery_colorpicker

from ticketing.jslib.jquery_validation_engine import validation_engine

def bootstrap_need():
    bootstrap.need()

class FanstaticDecoratorFactory(object):
    """ jsを追加するデコレータを作成するファクトリー
    """

    def __init__(self, *fns):
        self.fns = fns
    
    def add(self, fn):
        print "--- add"
        print fn
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
                print fn
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
    backbone.need
    )

with_wysiwyg_editor = FanstaticDecoratorFactory(
    tinymce.need
)

with_bootstrap = FanstaticDecoratorFactory(
    jquery.need,
    jquery_tools.need,
    json2.need,
    jqueryui.need,
    jquery_colorpicker.need,
    # black_tie.need,
    smoothness.need,
    underscore.need,
    backbone.need,
    bootstrap.need,
    timepicker.need,
 )

