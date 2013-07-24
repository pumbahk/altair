# -*- coding: utf-8 -*-
from altair.app.ticketing.resources import *

def includeme(config):
   config.add_route('dashboard.index'   , '/')

   config.scan(".")
