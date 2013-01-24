from .interfaces import IFileSession
from .core import FileSession

def get_filesession(request, name=""):
    return request.registry.getUtility(IFileSession, name=name)

def add_filesession(config, name="", make_path=None, prefix=None):
    ## todo: introspect, action
    assert make_path or prefix
    filesession = FileSession(prefix=prefix, make_path=make_path)
    return config.regitry.registerUtility(filesession, IFileSession, name=name)

def includeme(config):
    config.add_directive("add_filesession", add_filesession)
