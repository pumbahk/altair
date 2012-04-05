from zope.interface import implementer
from .interfaces import ITagSearchMap
from .manager import TagManager

@implementer(ITagSearchMap)
class TagSearchMap(dict):
    pass

def add_tagmanager(config, classifier, model=None, xref=None, tag=None):
    tsmap = config.registry.queryUtility(ITagSearchMap)

    model = config.maybe_dotted(model)
    xref = config.maybe_dotted(xref)
    tag = config.maybe_dotted(tag)

    if tsmap is None:
        tsmap = TagSearchMap()
        config.registry.registerUtility(tsmap, ITagSearchMap)
    tsmap[classifier] = TagManager(model, xref, tag)
