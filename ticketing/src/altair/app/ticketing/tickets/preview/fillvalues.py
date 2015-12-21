# -*- coding:utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import pystache
from pystache.context import ContextStack
from pystache.renderengine import RenderEngine
from collections import namedtuple
from . import TicketPreviewFillValuesException

class IndexedVariation(object):
    """ with colored and indexed string. like 10.{{fooo}}"""
    def __init__(self, style="fill:#015a01", ):
        self.style = style
        self.count = _CachedCounter(1)

    def rendering_string(self, name, v):
        i = self.count(name)
        fmt = u'<flowSpan style="%s">%s. </flowSpan>{{%s}}'
        return fmt % (self.style, i, name)

    padding = len(". </flowSpan>")
    def make_escape_method(self, renderer):
        default_escape = renderer.escape
        def escape(pair):
            try:
                midpoint = pair.index(". </flowSpan>{{")+self.padding
                prefix, x = pair[:midpoint], pair[midpoint:]
                # if x.startswith("{") and x.endswith("}"):
                #     return prefix + default_escape(x[1:-1])
                return prefix + default_escape(x)
            except ValueError:
                return default_escape(pair) # rendered string
        return escape


class IdentityVariation(object):
    """ no change output. like {{fooo}}"""
    def rendering_string(self, name, v):
        return u"{{%s}}" % name

    def make_escape_method(self, renderer):
        default_escape = renderer.escape
        def escape(x):
            # if x.startswith("{") and x.endswith("}"):
            #     return default_escape(x[1:-1])
            return default_escape(x)
        return escape

def template_collect_vars(template, variation=IdentityVariation()):
    """
    >>> template = u"{{hello}} this is a {{item}} {{{heee}}}"
    >>> template_collect_vars(template)
    set("hello", "item", "hee")
    """
    try:
        tokens = CollectVarsRenderEngine().parse(template)
        return {x.name for x in tokens if isinstance(x, RenderingVar)}
    except Exception, e:
        logger.exception(e)
        raise TicketPreviewFillValuesException(u"Templateからプレースホルダーを抽出する作業に失敗しました")

def template_fillvalues(template, params, variation=IdentityVariation()):
    """
    >>> template = u"{{hello}} this is a {{item}} {{{heee}}}"
    >>> template_fillvalues(template, {})
    u"{{hello}} this is a {{item}} {{heee}}"

    >>> template_fillvalues(template, {"hello": "good-bye, "})
    u"good-bye,  this is a {{item}} {{heee}}"
    """
    try:
        rendered = FillValuesRenderer(variation).render(template, convert_to_nested_dict(params))
        rendered = FillValuesRenderer(variation).render(rendered, convert_to_nested_dict(params))
        return rendered.replace(u"｛", u"{").replace(u"｝", u"}")
    except Exception, e:
        logger.exception(e)
        raise TicketPreviewFillValuesException(u"Templateへの文字列埋込みに失敗しました")

def convert_to_nested_dict(D, delim="."):
    r = D.copy()
    for k in r.keys():
        if delim in k:
            parts = k.split(delim);
            ptr = r
            for part in parts[:-1:1]:
                if not part in ptr:
                    ptr[part] = {}
                ptr = ptr[part]
            ptr[parts[-1]] = D[k]
    return r

class _CachedCounter(object):
    def __init__(self, default=0):
        self.c  = default
        self.m = {}
        self.default = default

    def __call__(self, name):
        if name in self.m:
            return self.m[name]
        v = self.m[name] = self.c
        self.c += 1
        return v

    def reset(self, default=None):
        self.m = {}
        self.c = self.default or default

class DefaultNoChangeContext(ContextStack):
    @classmethod
    def create(cls, variation_impl, *context, **kwargs):
        instance = super(DefaultNoChangeContext, cls).create(*context, **kwargs)
        instance.variation = variation_impl ##
        instance.__class__ = cls
        return instance

    def get(self, name, default=object()):
        v = super(DefaultNoChangeContext, self).get(name, default=default)
        if v == default:
            return self.variation.rendering_string(name, v) ##
        return v

class FillValuesRenderer(pystache.Renderer):
    """
    this is not perfect sollution:

    default(pystache):
      render "{{foo}} -- {{{bar}}}" with {} => " -- "

    FillValuesRenderer:
      render "{{foo}} -- {{{bar}}}" with {} => "{{foo}} -- {{bar}}"

    expected:
      render "{{foo}} -- {{{bar}}}" with {} => "{{foo}} -- {{{bar}}}"
    """
    def __init__(self, variation_impl, *args, **kwargs):
        super(FillValuesRenderer, self).__init__(*args, **kwargs)
        self.variation = variation_impl
        self.escape = variation_impl.make_escape_method(self) ##

    def _render_string(self, template, *context, **kwargs):
        """
        Render the given template string using the given context.

        """
        # RenderEngine.render() requires that the template string be unicode.
        template = self._to_unicode_hard(template)

        context = DefaultNoChangeContext.create(self.variation, *context, **kwargs)##
        self._context = context
        engine = self._make_render_engine()
        rendered = engine.render(template, context)

        return unicode(rendered)

RenderingVar = namedtuple("RenderingVar", "label name arg kwargs")

class FakeApply(object):
    def __init__(self, label):
        self.label = label

    def __call__(self, name, *args, **kwargs):
        return RenderingVar(self.label, name, args, kwargs)

class CollectVarsRenderEngine(RenderEngine):
    _make_get_literal = FakeApply("literal")
    _make_get_escaped = FakeApply("escaped")
    _make_get_partial = FakeApply("partial")
    _make_get_inverse = FakeApply("inverse")
    _make_get_section = FakeApply("section")
    def parse(self, template):
        return self._parse(template)._parse_tree
    def render(self, template, context):
        self.parse(template)

import re
DIGIT_RX = re.compile(r"([0-9]+)")
def natural_order_key(name):
    return [(int(x) if x.isdigit() else x) for x in re.split(DIGIT_RX, name) if x]

def natural_order(xs):
    return sorted(xs, key=natural_order_key)
