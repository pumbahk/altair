#!/usr/bin/env python
import os
import sadisplay

"""
find . -name "models.py" | grep -v tests | sed 's/^.*altaircms/import altaircms/g; s/\//./g; s/\.py/ as models\nadd(model_instances, models, dir(models))/g'
"""
import inspect
from altaircms.models import Base

def add(r, m, cands):
    for k in cands:
        if not k in r:
            v = getattr(m, k)
            if inspect.isclass(v) and issubclass(v, Base):
                r[k] = v
    return r
    
model_instances = {}
import altaircms.plugins.widget.countdown.models as models
add(model_instances, models, dir(models))
import altaircms.plugins.widget.image.models as models
add(model_instances, models, dir(models))
import altaircms.plugins.widget.menu.models as models
add(model_instances, models, dir(models))
import altaircms.plugins.widget.detail.models as models
add(model_instances, models, dir(models))
import altaircms.plugins.widget.performancelist.models as models
add(model_instances, models, dir(models))
import altaircms.plugins.widget.reuse.models as models
add(model_instances, models, dir(models))
import altaircms.plugins.widget.calendar.models as models
add(model_instances, models, dir(models))
import altaircms.plugins.widget.flash.models as models
add(model_instances, models, dir(models))
import altaircms.plugins.widget.breadcrumbs.models as models
add(model_instances, models, dir(models))
import altaircms.plugins.widget.summary.models as models
add(model_instances, models, dir(models))
import altaircms.plugins.widget.movie.models as models
add(model_instances, models, dir(models))
import altaircms.plugins.widget.freetext.models as models
add(model_instances, models, dir(models))
import altaircms.plugins.widget.ticketlist.models as models
add(model_instances, models, dir(models))
import altaircms.plugins.widget.topic.models as models
add(model_instances, models, dir(models))
import altaircms.auth.models as models
add(model_instances, models, dir(models))
import altaircms.asset.models as models
add(model_instances, models, dir(models))
import altaircms.widget.models as models
add(model_instances, models, dir(models))
import altaircms.page.models as models
add(model_instances, models, dir(models))
import altaircms.usersetting.models as models
add(model_instances, models, dir(models))
import altaircms.models as models
add(model_instances, models, dir(models))
import altaircms.topic.models as models
add(model_instances, models, dir(models))
import altaircms.layout.models as models
add(model_instances, models, dir(models))
import altaircms.tag.models as models
add(model_instances, models, dir(models))

desc = sadisplay.describe(model_instances.values())
open('schema.plantuml', 'w').write(sadisplay.plantuml(desc))
open('schema.dot', 'w').write(sadisplay.dot(desc))
os.system("dot -Tpng schema.dot > schema.png")
