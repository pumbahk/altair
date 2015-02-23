# -*- coding:utf-8 -*-
import logging

import json
import urllib2

logger = logging.getLogger(__name__)

def on_order_canceled(ev):
    try:
        order_no = ev.order.order_no
        res_text = create(request=ev.request, data=data)
        # TODO: resどうする?
    except Exception, e:
        logger.error(e.message, exc_info=1)
        raise

def create(request, data):
    settings = request.registry.settings
    api_url = settings.get('orion.create_url')
    if api_url is None:
        raise Exception("orion.api_uri is None")
    
    data = json.dumps(data)
    logger.info("Create request to Orion API: %s" % data);

    req = urllib2.Request(api_url, data, headers={ u'Content-Type': u'text/json; charset="UTF-8"' })
    try:
        stream = urllib2.urlopen(req);
        headers = stream.info()
        if stream.code == 200:
            res = unicode(stream.read(), 'utf-8')
            logger.info("response = %s" % res)
            return json.loads(res)
        else:
            raise Exception("server returned unexpected status: %d (payload) %r" % (stream.code, stream.read()))
    except Exception, e:
        raise Exception("cannot connect to %s" % api_url)

def search(request, data):
    settings = request.registry.settings
    api_url = settings.get('orion.search_url')
    if api_url is None:
        raise Exception("orion.search_uri is None")
    
    data = json.dumps(data)
    logger.info("Create request to Orion API: %s" % data)
    
    req = urllib2.Request(api_url, data, headers={ u'Content-Type': u'text/json; charset="UTF-8"' })
    try:
        stream = urllib2.urlopen(req);
        if stream.code == 200:
            res = unicode(stream.read(), 'utf-8')
            logger.info("response = %s" % res)
            return json.loads(res)
        else:
            raise Exception("Orion API returned code %u" % stream.code)
    except Exception, e:
        raise Exception("cannot connect to %s" % api_url)
