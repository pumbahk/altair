from . import helpers
from . import api

def add_helpers(event):
    event["h"] = helpers
    event["_api"] = api
