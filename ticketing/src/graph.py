#!/usr/bin/env python
import os
import sadisplay
import inspect

from altair.app.ticketing.models import Base

def add(r, m, cands):
    for k in cands:
        if not k in r:
            v = getattr(m, k)
            if inspect.isclass(v) and issubclass(v, Base):
                r[k] = v
    return r

model_instances = {}

import altair.app.ticketing.models as models
add(model_instances, models, dir(models))
import altair.app.ticketing.oauth2.models as models
add(model_instances, models, dir(models))
import altair.app.ticketing.master.models as models
add(model_instances, models, dir(models))
import altair.app.ticketing.oauth2.models as models
add(model_instances, models, dir(models))
import altair.app.ticketing.operators.models as models
add(model_instances, models, dir(models))
import altair.app.ticketing.orders.models as models
add(model_instances, models, dir(models))
import altair.app.ticketing.users.models as models
add(model_instances, models, dir(models))
import altair.app.ticketing.core.models as models
add(model_instances, models, dir(models))


desc = sadisplay.describe(model_instances.values())
open('schema.plantuml', 'w').write(sadisplay.plantuml(desc))
open('schema.dot', 'w').write(sadisplay.dot(desc))

os.system("dot -Tpdf schema.dot > ../docs/images/schema.pdf")
