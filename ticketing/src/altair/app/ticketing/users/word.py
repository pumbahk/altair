# -*- coding:utf-8 -*-

import logging

from altair.app.ticketing.cart import api as cart_api
from altair.app.ticketing.api.impl import CMSCommunicationApi, SiriusCommunicationApi
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
        logger.warn("user is None in word_subscribe()")
        return

    if user.id is None:
        logger.warn("user.id is None in word_subscribe()")
        return

    if word_ids is None or len(word_ids) == 0:
        logger.warn("word_ids is none or empty array in word_subscribe()")
        return

    words = get_word(request, id=' '.join([ str(x) for x in word_ids ]))

    logger.debug("word_subscribe: %s" % ' '.join([ str(x) for x in word_ids ]))
    for word in words:
        if WordSubscription.query.filter(WordSubscription.user_id==user.id, WordSubscription.word_id==word['id']).first() is None:
            session.add(WordSubscription(user_id=user.id, word_id=word['id']))


def get_word(request, id=None, q=None):
    communication_api = cart_api.get_communication_api(request, CMSCommunicationApi)
    if id is not None and 0 < len(id):
        path = "/api/word/?id=%(id)s" % {"id": urllib.quote_plus(id)}
    elif q is not None and 0 < len(q):
        path = "/api/word/?q=%(q)s&backend_organization_id=%(org_id)d" % {"q": urllib.quote_plus(q), "org_id": request.context.organization.id}
    else:
        raise Exception("invalid param")

    if request.organization.setting.migrate_to_sirius:
        # Siriusからお気に入りワードを取得する。Siriusが安定するまではSirius APIが失敗したら旧CMS APIを実行する
        # Siriusが安定したらSiriusのみに通信するよう修正すること。
        # 本処理ブロックを削除し、communication_apiをSirius向けに生成すれば良い
        sirius_communication_api = cart_api.get_communication_api(request, SiriusCommunicationApi)
        sirius_req = sirius_communication_api.create_connection(path)
        try:
            with contextlib.closing(urllib2.urlopen(sirius_req)) as sirius_res:
                data = sirius_res.read()
                logger.info('sirius API call complete: {}'.format(data))
                result = json.loads(data)
                return result['words']
        except Exception as e:  # Sirius APIが失敗した場合、以降の旧CMS APIのレスポンスを採用
            logging.error('*sirius api* failed: url=%s, reason=%s', sirius_communication_api.get_url(path),
                          e, exc_info=1)

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
