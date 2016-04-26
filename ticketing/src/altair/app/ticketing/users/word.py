# -*- coding:utf-8 -*-

import logging

from altair.app.ticketing.cart import api as cart_api
from altair.app.ticketing.api.impl import CMSCommunicationApi
import sqlahelper

from altair.app.ticketing.users.models import WordSubscription

import urllib
import urllib2
import contextlib
import json

logger = logging.getLogger(__name__)

session = sqlahelper.get_session()

def word_subscribe(request, user, word_ids):
    if user is None:
        logger.error("user is None in word_subscribe()")
        return

    words = get_word(request, id=' '.join([ str(x) for x in word_ids ]))

    logger.debug("word_subscribe: %s" % ' '.join([ str(x) for x in word_ids ]))
    for word in words:
        if WordSubscription.query.filter(WordSubscription.user_id==user.id, WordSubscription.word_id==word['id']).first() is None:
            session.add(WordSubscription(user_id=user.id, word_id=word['id']))

def get_word(request, id=None, q=None):
    communication_api = cart_api.get_communication_api(request, CMSCommunicationApi)
    if id is not None:
        path = "/api/word/?id=%(id)s" % {"id": urllib.quote_plus(id)}
    elif q is not None and 0 < len(q):
        path = "/api/word/?q=%(q)s" % {"q": urllib.quote_plus(q)}
    else:
        raise Exception("invalid param")

    req = communication_api.create_connection(path)
    try:
        with contextlib.closing(urllib2.urlopen(req)) as res:
            try:
                data = res.read()
                logger.info("API call complete: %s" % data)
                result = json.loads(data)
                return result['words']
            except urllib2.HTTPError, e:
                logging.warn("*api* HTTPError: url=%s errorno %s" % (communication_api.get_url(path), e))
    except urllib2.URLError, e:
        fmt = "*api* URLError: url=%s response status %s"
        logging.warn(fmt % (communication_api.get_url(path), e))
    return [ ]
