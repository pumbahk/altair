# -*- coding:utf-8 -*-
#!/usr/bin/env python
import os
import sadisplay
import pkg_resources as p
import inspect
from altaircms.models import Base

def _filepath_to_modulename(root, rootmodule, path):
    replaced = path.replace(root, rootmodule)
    return os.path.splitext(replaced)[0].replace("/", ".")

def add(r, m, cands):
    for k in cands:
        if not k in r:
            v = getattr(m, k)
            if inspect.isclass(v) and issubclass(v, Base):
                r[k] = v
    return r

def _import(mname):
    m = __import__(mname)
    if not "." in mname:
        return m
    for subname in mname.split(".")[1:]:
        m = getattr(m, subname)
    return m

model_instances = {}
rootmodule = "altaircms"
root = p.resource_filename(rootmodule, "")
for prefix, dirs, files in  os.walk(root):
    for f in files:
        if f.endswith("models.py") and not "tests" in f:
            modulepath = os.path.join(prefix, f)
            mname = _filepath_to_modulename(root, rootmodule, modulepath)
            m = _import(mname)
            add(model_instances, m, dir(m))

desc = sadisplay.describe(model_instances.values())
open('schema.plantuml', 'w').write(sadisplay.plantuml(desc))
open('schema.dot', 'w').write(sadisplay.dot(desc))
os.system("dot -Tsvg schema.dot > dbschema.svg")


