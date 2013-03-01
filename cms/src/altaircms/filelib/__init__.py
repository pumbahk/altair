from .interfaces import IFileSession
from .core import FileSession, File

__all__ = ["File", 
           "FileSession", 
           "get_filesession", 
           "add_filesession", 
           ]

def get_filesession(request, name=""):
    return request.registry.getUtility(IFileSession, name=name)

def add_filesession(config, session, name=""):
    ## todo: introspect, action
    assert session.make_path or session.prefix
    return config.registry.registerUtility(session, IFileSession, name=name)

def includeme(config):
    config.add_directive("add_filesession", add_filesession)
