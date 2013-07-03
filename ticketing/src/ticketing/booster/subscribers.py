from . import helpers
from . import api
from .api import load_user_profile
from .api import set_user_profile_for_order

def add_helpers(event):
    event["h"] = helpers
    event["_api"] = api

def add_simple_layout(event):
    event["layout"] = event["request"].layout


def on_order_completed(event):
    order = event.order

    user_profile = load_user_profile(event.request)
    set_user_profile_for_order(event.request, order, user_profile)
