# -*- encoding:utf-8 -*-
import sys
import argparse
import inspect
import os.path
from pkg_resources import resource_filename, EntryPoint


usage = u"""\
Load data from csv file\n

how to use
---------------
<program> --target=altaircms.models:Performance --infile=input.csv

"""

parser = argparse.ArgumentParser(description="Load data from csv file", epilog=usage, formatter_class=argparse.RawDescriptionHelpFormatter,)

parser.add_argument('--infile', nargs='?', type=argparse.FileType('r'),
                     default=sys.stdin)
parser.add_argument('--outfile', nargs='?', type=argparse.FileType('w'),
                     default=sys.stdout)
parser.add_argument("--target")
parser.add_argument("--dburl", default="sqlite://")

parser.add_argument("--list", action="store_const", const=bool)
parser.add_argument("--rootmodule", default="altaircms")
parser.add_argument("--modelbase", default="altaircms.models:Base")
parser.add_argument("--verbose", default=False, action="store_const", const=bool)

def import_symbol(symbol):
    """import a content of module from a module name string

    module name string format:
      foo.bar.baz:symbol_name 
      foo.bar.baz
    """
    return EntryPoint.parse("x=%s" % symbol).load(False)


def collect_models(model_file_path, rootmodule, root, modelbase):
    module = import_symbol(moduleformat(root, rootmodule, model_file_path))

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


def collect_model_mapping(rootmodule, modelbase):
    _history = set()
    root = resource_filename(rootmodule, "")

    modelnames = []

    for path in collect_files(root, lambda f: f.endswith("models.py") and not "test" in f):
        for m in collect_models(path, rootmodule, root, modelbase):
            if not hasattr(m, "__tablename__"):
                continue
            if m.__tablename__ in _history:
                continue

            _history.add(m.__tablename__)

            modelnames.append((m, "%s:%s" % (m.__module__, m.__name__)))
    return modelnames


def list_modelnames(args):
    args.modelbase = import_symbol(args.modelbase)
    models = collect_model_mapping(args.rootmodule, args.modelbase)

    if args.verbose:
        for m, modelname in sorted(models, key=lambda x : x[1]):
            colms = u", ".join([c.name for c in model_columns(m)])
            print modelname, colms
    else:
        for m, modelname in sorted(models, key=lambda x : x[1]):
            print modelname
        



### load csv

_CACHE = {}
def model_columns(model):
    if model in _CACHE:
        return _CACHE[model]
    else:
        _CACHE[model] = sorted((c for c in model.__mapper__.columns), key=lambda c: c.name)
        return _CACHE[model]


def load_from_csv(args):
    pass


def main(args):
    if args.list:
        list_modelnames(args)
    else:
        load_from_csv(args)


args = parser.parse_args()
main(args)

