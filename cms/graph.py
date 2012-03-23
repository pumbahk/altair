#!/usr/bin/env python
import os
import sadisplay


"""
現在、全てのmodelを取得できない。
find . -name "models.py" | sed 's/^.*altaircms/import altaircms/g; s/\//./g; s/\.py/ as models\ndesc.extend(sadisplay.describe([getattr(models, attr) for attr in dir(models)]))/g'
"""
desc = []
from altaircms import models
desc.extend(sadisplay.describe([getattr(models, attr) for attr in dir(models)]))
open('schema.plantuml', 'w').write(sadisplay.plantuml(desc))
open('schema.dot', 'w').write(sadisplay.dot(desc))

os.system("dot -Tpng schema.dot > schema.png")
