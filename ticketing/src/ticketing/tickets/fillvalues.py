import pystache
from pystache.context import ContextStack
from pystache.renderengine import RenderEngine
from collections import namedtuple

def template_collect_vars(template):
    """
    >>> template = u"{{hello}} this is a {{item}} {{{heee}}}"
    >>> template_collect_vars(template)
    set("hello", "item", "hee")
    """
    tokens = CollectVarsRenderEngine().parse(template)
    return {x.name for x in tokens if isinstance(x, RenderingVar)}

def template_fillvalues(template, params):
    """
    >>> template = u"{{hello}} this is a {{item}} {{{heee}}}"
    >>> template_fillvalues(template, {})
    u"{{hello}} this is a {{item}} {{heee}}"    

    >>> template_fillvalues(template, {"hello": "good-bye, "})
    u"good-bye,  this is a {{item}} {{heee}}"    
    """
    return FillValuesRenderer().render(template, params)


class DefaultNoChangeContext(ContextStack):
    @classmethod
    def create(cls, *context, **kwargs):
        instance = super(DefaultNoChangeContext, cls).create(*context, **kwargs)
        instance.__class__ = cls
        return instance

    def get(self, name, default=object()):
        v = super(DefaultNoChangeContext, self).get(name, default=default)
        return u"{{%s}}" % name if v == default else v

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

    def _render_string(self, template, *context, **kwargs):
        """
        Render the given template string using the given context.

        """
        # RenderEngine.render() requires that the template string be unicode.
        template = self._to_unicode_hard(template)

        context = DefaultNoChangeContext.create(*context, **kwargs)
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
