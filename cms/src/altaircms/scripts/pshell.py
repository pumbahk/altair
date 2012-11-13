# -*- encoding:utf-8 -*-
import inspect
import os.path
import transaction

from pkg_resources import resource_filename, EntryPoint

def import_symbol(symbol):
    """import a content of module from a module name string

    module name string format:
      foo.bar.baz:symbol_name 
      foo.bar.baz
    """
    return EntryPoint.parse("x=%s" % symbol).load(False)


def collect_models(module, modelbase):
    for x in module.__dict__.values():
        if inspect.isclass(x) and issubclass(x, modelbase):
            yield x


def collect_files(root, p):
    for prefix, dires, files in os.walk(root):
        for f in files:
            if p(f):
                fullpath = os.path.join(prefix, f)
                yield fullpath


def moduleformat(root, rootmodule, path):
    """foo/bar/baz.py -> foo.bar.baz"""
    replaced = path.replace(root, rootmodule)
    return os.path.splitext(replaced)[0].replace("/", ".")

##
def setup(env):
    import altaircms
    from altaircms.models import DBSession, Base
    env["S"] =  DBSession
    env["T"] = transaction
    env["Base"] =  Base
    env["M"] = Base.metadata

    rootmodule = "altaircms"
    root = resource_filename(rootmodule, "")
    for path in collect_files(altaircms.__path__[0], lambda f: f.endswith("models.py") and not "test" in f):
        module = import_symbol(moduleformat(root, rootmodule, path))
        for m in collect_models(module, Base):
            env[m.__name__] = m


