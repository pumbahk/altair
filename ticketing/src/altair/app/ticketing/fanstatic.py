# -*- coding:utf-8 -*-

from pyramid.interfaces import IRequest
from js.jquery import jquery
from js.underscore import underscore
from js.jquery_tools import jquery_tools
from js.json2 import json2
# from js.jqueryui import black_tie
from js.jqueryui import jqueryui
from js.tinymce import tinymce
from js.backbone import backbone
from js.bootstrap_ts import bootstrap, bootstrap_responsive_css
from js.jquery_cookie import cookie
from js.jqgrid_ts import jqgrid, jqgrid_i18n_en
from js.jqueryui_bootstrap import jqueryui_bootstrap
from js.bootstrap_datepicker_ts import bootstrap_datepicker
from js.i18n import i18n
import venusian
import types

from altair.app.ticketing.jslib.jquery_validation_engine import validation_engine

def bootstrap_need():
    bootstrap.need()

class FanstaticDecoratorFactory(object):
    """ jsを追加するデコレータを作成するファクトリー
    """

    venusian = venusian

    def __init__(self, *fns, **options):
        self.fns = set(fns)
        self.predicates = options.get('predicates', [])

    def __add__(self, that):
        return self.merge(that)

    def add(self, fn):
        new = FanstaticDecoratorFactory()
        new.fns = set(self.fns)
        new.fns.add(fn)
        return new

    def update(self, other):
        self.fns.update(other.fns)

    def merge(self, other):
        new = FanstaticDecoratorFactory(*self.fns)
        new.update(other)
        return new

    def when(self, *predicates):
        return FanstaticDecoratorFactory(*self.fns, predicates=predicates)

    def not_when(self, *predicates):
        return FanstaticDecoratorFactory(*self.fns, predicates=[lambda request: not predicate(request) for predicate in predicates])

    ## @todo: support venusian
    def attach(self, wrapped):
        info = self.venusian.attach(wrapped, category='altair.ticketing', callback=lambda context, name, ob: 0)
        def wraps(*args, **kwargs):
            request = None
            if len(args) >= 2:
                if IRequest.providedBy(args[1]):
                    request = args[1]
            elif len(args) >= 1:
                if IRequest.providedBy(args[0]):
                    request = args[0]
                else:
                    if info.scope == 'class':
                        # XXX: view class に request という attribute があることを暗黙に期待
                        # (interface で縛る方が良い?)
                        _request = getattr(args[0], 'request', None)
                        if _request is not None and IRequest.providedBy(_request):
                            request = _request

            # call the view function
            response = wrapped(*args, **kwargs)

            if (request is None and not self.predicates) or all(predicate(request) for predicate in self.predicates):
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

with_jquery_tools = FanstaticDecoratorFactory(
    jquery_tools.need
    )

with_fanstatic_jqueries = FanstaticDecoratorFactory(
    jquery.need,
    jquery_tools.need,
    json2.need,
    underscore.need,
    backbone.need
    )

with_jqueryui = FanstaticDecoratorFactory(
    jqueryui.need,
    jqueryui_bootstrap.need
    )

with_wysiwyg_editor = FanstaticDecoratorFactory(
    tinymce.need
    )

with_bootstrap = FanstaticDecoratorFactory(
    jquery.need,
    jquery_tools.need,
    json2.need,
    cookie.need,
    underscore.need,
    backbone.need,
    bootstrap.need,
    bootstrap_responsive_css.need,
    bootstrap_datepicker.need,
    i18n.need,
    jqgrid.need,
    jqgrid_i18n_en.need
    )

