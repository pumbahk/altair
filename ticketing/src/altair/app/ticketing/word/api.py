# encoding: utf-8

import isodate
from datetime import datetime
import json
import hashlib
from . import VISIBLE_EVENT_SESSION_KEY


def get_cms_word_data(request, now=None):
    now = now or datetime.now()
    data = event.get_cms_data(request, now)
    hashed_value = hashlib.sha1(json.dumps(data)).hexdigest()
    if request.session.get("cms_send_data"):
        if request.session.get("cms_send_data") == hashed_value:
            raise Exception("same data is already sent.")

    request.session["cms_send_data"] = hashed_value
    return {
        'organization': {'id': organization.id,
                         'short_name': organization.short_name,
                         "code": organization.code},
        'events':[data],
        'created_at':isodate.datetime_isoformat(now),
        'updated_at':isodate.datetime_isoformat(now),
    }
