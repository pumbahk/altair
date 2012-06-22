# -*- coding: utf-8 -*-

import json
import urllib2
import logging
import contextlib

logger = logging.getLogger(__file__)
from ..api.impl import get_communication_api
from ..api.impl import CMSCommunicationApi

## todo: 粗結合
def get_event_info_from_cms(request, event_id):
    communication_api = get_communication_api(request, CMSCommunicationApi)
    url = "/api/event/%(event_id)s/info" % {"event_id": event_id}
    req = communication_api.create_connection(url)

    res = None
    try:
        res = urllib2.urlopen(req)
        data = res.read()
    except urllib2.HTTPError, e:
        logger.info("*api* cms event api info is not found(url=%s)" % url)
    except Exception, e:
        logger.exception(e)
    finally:
        res.close()
    return {}
