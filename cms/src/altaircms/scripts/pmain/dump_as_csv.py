# -*- encoding:utf-8 -*-

import codecs
import sys
sys.stdout = codecs.getwriter("utf-8")(sys.stdout)

import inspect
from pkg_resources import resource_filename, EntryPoint
import os.path
import csv

from altaircms.models import Base
from altaircms.models import DBSession
from datetime import datetime

def moduleformat(root, rootmodule, path):
    """foo/bar/baz.py -> foo.bar.baz"""
    replaced = path.replace(root, rootmodule)
    return os.path.splitext(replaced)[0].replace("/", ".")

def import_symbol(symbol):
    """import a content of module from a module name string

    module name string format:
      foo.bar.baz:symbol_name 
      foo.bar.baz
    """
    return EntryPoint.parse("x=%s" % symbol).load(False)

def collect_files(root, p):
    for prefix, dires, files in os.walk(root):
        for f in files:
            if p(f):
                fullpath = os.path.join(prefix, f)
                yield fullpath
                

def collect_models(model_file_path, rootmodule, root):
    module = import_symbol(moduleformat(root, rootmodule, model_file_path))

    for x in module.__dict__.values():
        if inspect.isclass(x) and issubclass(x, Base):
            yield x

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


def mapping(v):
    if isinstance(v, datetime):
        return v.strftime("%Y-%m-%d %H:%M:%S")
    else:
        return unicode(v).encode("utf-8")

def query_dump_as_csv(model, qs, oport, noid=False):
    outcsv = csv.writer(oport)
    for q in qs:
        cols = [mapping(getattr(q, c.name)) for c in model_columns(model)]
        if noid:
            cols[0] = "None"
        outcsv.writerow(cols)

def model_dump_as_csv(model, oport, noid=False):
    return query_dump_as_csv(model, model_query(model), oport)

def model_query(model):
    if hasattr(model, "query"):
        return model.query
    else:
        return DBSession.query(model)


def main(*args, **kwargs):
    history = set()

    rootmodule = "altaircms"
    root = resource_filename(rootmodule, "")

    with open("master.txt", "w") as master_w:
        for path in collect_files(root, lambda f: f.endswith("models.py") and not "test" in f):
            for m in collect_models(path, rootmodule, root):

                if not hasattr(m, "__tablename__"):
                    continue
                if m.__tablename__ in history:
                    continue
                history.add(m.__tablename__)

                master_w.write("\n============\n")
                master_w.write(m.__tablename__)
                master_w.write("\n============\n")
                master_w.write(", ".join([c.name for c in model_columns(m)]))
                master_w.write("\n")

                with open(m.__tablename__+".csv", "w") as w:
                    model_dump_as_csv(m, w)
