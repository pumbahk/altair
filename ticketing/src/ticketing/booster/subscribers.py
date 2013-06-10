from . import helpers
from . import api

def add_helpers(event):
    event["h"] = helpers
    event["_api"] = api

def add_simple_layout(event):
    event["layout"] = event["request"].layout
