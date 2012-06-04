#!/usr/bin/env python

import os
import sadisplay
import inspect

from ticketing.models import Base

def add(r, m, cands):
    for k in cands:
        if not k in r:
            v = getattr(m, k)
            if inspect.isclass(v) and issubclass(v, Base):
                r[k] = v
    return r

model_instances = {}

import ticketing.oauth2.models as models
add(model_instances, models, dir(models))
import ticketing.organizations.models as models
add(model_instances, models, dir(models))
import ticketing.events.models as models
add(model_instances, models, dir(models))
import ticketing.master.models as models
add(model_instances, models, dir(models))
import ticketing.oauth2.models as models
add(model_instances, models, dir(models))
import ticketing.operators.models as models
add(model_instances, models, dir(models))
import ticketing.orders.models as models
add(model_instances, models, dir(models))
import ticketing.products.models as models
add(model_instances, models, dir(models))
import ticketing.users.models as models
add(model_instances, models, dir(models))
import ticketing.venues.models as models
add(model_instances, models, dir(models))

def main(env, args):

    desc = sadisplay.describe(model_instances.values())
    open('schema.plantuml', 'w').write(sadisplay.plantuml(desc))
    open('schema.dot', 'w').write(sadisplay.dot(desc))

    os.system("dot -Tpdf schema.dot > ../docs/images/schema.pdf")
