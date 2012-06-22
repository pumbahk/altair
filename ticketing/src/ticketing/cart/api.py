# -*- coding: utf-8 -*-

import isodate
import json
import logging
import urllib2
from datetime import datetime

from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPCreated
from pyramid.threadlocal import get_current_registry
from pyramid.url import route_path

from ticketing.models import DBSession
from ticketing.core.models import Event

      
def get_cms_api_connection(request, path, params):
    return request.registry.queryUtility(ICommunicationApi, CMSCommunicationApi)


## todo: 粗結合
def get_event_info_from_cms(request, event):
    settings = request.registry.settings
    settings.get("altaircms.event.notification_url")

    url = settings.get('altaircms.event.notification_url') + 'api/event/register'
    req = urllib2.Request(url, json.dumps(data))
    req.add_header('X-Altair-Authorization', settings.get('altaircms.apikey'))
    req.add_header('Connection', 'close')

    try:
        res = urllib2.urlopen(req)
        if res.getcode() == HTTPCreated.code:
            request.session.flash(u'イベントをCMSへ送信しました')
        else:
            raise urllib2.HTTPError(code=res.getcode())
    except urllib2.HTTPError, e:
        logging.warn("cms sync http error: response status (%s) %s" % (e.code, e.read()))
        request.session.flash(u'イベント送信に失敗しました (%s)' % e.code)
    except Exception, e:
        logging.error("cms sync error: %s, %s" % (e.reason, e.message))
        request.session.flash(u'イベント送信に失敗しました')

    return HTTPFound(location=route_path('events.show', request, event_id=event.id))
