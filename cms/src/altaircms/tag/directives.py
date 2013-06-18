from .interfaces import ITagManager
from .interfaces import ISystemTagManager
from .manager import TagManager
from .manager import SystemTagManager

def add_tagmanager(config, name, model=None, xref=None, tag=None):
    model = config.maybe_dotted(model)
    xref = config.maybe_dotted(xref)
    tag = config.maybe_dotted(tag)
    manager = TagManager(model, xref, tag)
    config.registry.registerUtility(manager, ITagManager, name)

    system_manager = SystemTagManager(model, xref, tag)
    config.registry.registerUtility(system_manager, ISystemTagManager, name)
