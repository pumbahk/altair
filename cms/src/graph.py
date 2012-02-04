#!/usr/bin/env python
import os
import sadisplay
from altaircms import models

desc = sadisplay.describe([getattr(models, attr) for attr in dir(models)])
open('schema.plantuml', 'w').write(sadisplay.plantuml(desc))
open('schema.dot', 'w').write(sadisplay.dot(desc))

os.system("dot -Tpng schema.dot > schema.png")
