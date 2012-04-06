from .interfaces import ITagManager
from .manager import TagManager

def add_tagmanager(config, name, model=None, xref=None, tag=None):
    model = config.maybe_dotted(model)
    xref = config.maybe_dotted(xref)
    tag = config.maybe_dotted(tag)
    manager = TagManager(model, xref, tag)
    config.registry.registerUtility(manager, ITagManager, name)


