#!/usr/bin/env python
import os
import sadisplay

desc = []
import ticketing.oauth2.models as models
print [getattr(models, attr) for attr in dir(models)]
desc.extend(sadisplay.describe([getattr(models, attr) for attr in dir(models)]))
# ..models as modelsndesc.extend(sadisplay.describe([getattr(models, attr) for attr in dir(models)]))
import ticketing.clients.models as models
desc.extend(sadisplay.describe([getattr(models, attr) for attr in dir(models)]))
import ticketing.events.models as models
desc.extend(sadisplay.describe([getattr(models, attr) for attr in dir(models)]))
import ticketing.master.models as models
desc.extend(sadisplay.describe([getattr(models, attr) for attr in dir(models)]))
import ticketing.oauth2.models as models
desc.extend(sadisplay.describe([getattr(models, attr) for attr in dir(models)]))
import ticketing.operators.models as models
desc.extend(sadisplay.describe([getattr(models, attr) for attr in dir(models)]))
import ticketing.orders.models as models
desc.extend(sadisplay.describe([getattr(models, attr) for attr in dir(models)]))
import ticketing.products.models as models
desc.extend(sadisplay.describe([getattr(models, attr) for attr in dir(models)]))
import ticketing.users.models as models
desc.extend(sadisplay.describe([getattr(models, attr) for attr in dir(models)]))
import ticketing.venues.models as models
desc.extend(sadisplay.describe([getattr(models, attr) for attr in dir(models)]))


# desc = sadisplay.describe([getattr(models, attr) for attr in dir(models)])
open('schema.plantuml', 'w').write(sadisplay.plantuml(desc))
open('schema.dot', 'w').write(sadisplay.dot(desc))

os.system("dot -Tpdf schema.dot > ../docs/images/schema.pdf")
