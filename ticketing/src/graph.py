#!/usr/bin/env python
import os
import sadisplay
from ticketing import models

desc = sadisplay.describe([getattr(models, attr) for attr in dir(models)])
open('schema.plantuml', 'w').write(sadisplay.plantuml(desc))
open('schema.dot', 'w').write(sadisplay.dot(desc))

os.system("dot -Tpdf schema.dot > ../docs/images/schema.pdf")
