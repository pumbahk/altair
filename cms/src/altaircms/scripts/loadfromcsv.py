# -*- encoding:utf-8 -*-
import sys
import argparse
import inspect
import os.path
import csv
import transaction
from datetime import datetime
import re

from pkg_resources import resource_filename, EntryPoint

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
            print modelname, m.__tablename__, "@", colms
    else:
        for m, modelname in sorted(models, key=lambda x : x[1]):
            print modelname
        



### load csv
_CACHE = {}
def model_columns(model):
    if model in _CACHE:
        return _CACHE[model]
    else:
        ## フィールドはアルファベット順に取り出す。ただしidは先頭
        ## e.g. id, boolean,  point, score

        id_index = None
        cs = sorted((c for c in model.__mapper__.columns), key=lambda c: c.name)

        for i, c in enumerate(cs):
            if  c.name == "id":
                id_index = i

        if id_index:
            cs.insert(0, cs.pop(id_index))
        _CACHE[model] = cs
        return _CACHE[model]

def setup(args):
    import sqlahelper
    import sqlalchemy as sa

    engine = sa.create_engine(args.dburl)
    engine.echo = True

    sqlahelper.add_engine(engine)

    args.modelbase = import_symbol(args.modelbase)
    collect_model_mapping(args.rootmodule, args.modelbase)

    # sqlahelper.get_base().metadata.create_all()
    return sqlahelper.get_session()

DATETIME_RX = re.compile("\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")  # 2012-05-25 22:34:35
def string_to_value(obj, colname, v):
    if "None" == v:
        return None
    elif "True" == v:
        return True
    elif "False" == v:
        return False
    elif DATETIME_RX.search(v):
        return datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
    else:
        return v.decode("utf-8")

def load_from_csv(mapper, args):
    reader = csv.reader(args.infile, quotechar="'")
    model = import_symbol(args.target)
    cols = [c.name for c in model_columns(model)]

    session = setup(args)

    for row in reader:
        obj = model()
        for c, v in  zip(cols, row):
            setattr(obj, c, mapper(obj, c, v))

        session.add(obj)


def main():
    usage = u"""\
    Load data from csv file\n

    -----------
    example
    -----------

    insert
    ----------------------------------------
    %(prog)s --dburl="sqlite://" altaircms.models:Performance #from stdin
    %(prog)s --dburl="sqlite://" altaircms.models:Performance input.csv #from file
    
    listing target candidates
    ----------------------------------------
    %(prog)s --list
    %(prog)s --list --verbose
    %(prog)s --list --rootmodule=ticketing --modelbase=ticketing.models:Base

    """

    parser = argparse.ArgumentParser(description="Load data from csv file", epilog=usage, formatter_class=argparse.RawDescriptionHelpFormatter,)

    parser.add_argument("target", help=u"target model class name with `some.module:ModelName'", nargs="?")
    parser.add_argument('infile', help=u"csv file", nargs='?', type=argparse.FileType('r'),
                         default=sys.stdin)
    parser.add_argument('--outfile', nargs='?', type=argparse.FileType('w'),
                         default=sys.stdout)
    parser.add_argument("--dburl", help="db url. e.g. mysql+pymysql://foo:foo@localhost/foo (default: %(default)s)", default="sqlite://")

    parser.add_argument("--list", help="listing target model class candidates", action="store_const", const=bool)
    parser.add_argument("--rootmodule", help="root of module (default: %(default)s)", default="altaircms")
    parser.add_argument("--modelbase", help="model base class name (default: %(default)s)", default="altaircms.models:Base")
    parser.add_argument("--verbose", default=False, action="store_const", const=bool)

    args = parser.parse_args()
    _main(args)

def _main(args):
    if args.list:
        return list_modelnames(args)
    try:
        load_from_csv(string_to_value, args)
        transaction.commit()
    except:
        raise 
        transaction.abort()
    return 0

if __name__ == "__main__":
    main()
