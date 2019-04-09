from altair.app.ticketing.orderreview import api, helpers


def add_helpers(event):
    event["h"] = helpers
    event["_api"] = api
