# -*- coding:utf-8 -*-

import threading
import logging
from pyramid.threadlocal import get_current_request
from sqlalchemy import event
from sqlalchemy.engine.base import Engine

logger = logging.getLogger(__name__)
lock = threading.Lock()

def includeme(config):
    config.add_tween('altair.queryprofile.QueryCountTween')


@event.listens_for(Engine, "after_cursor_execute")
def _after_cursor_execute(conn, cursor, stmt, params, context, execmany):
    request = get_current_request()
    if request is not None:
        with lock:
            count = request.environ.get('altair.queryprofile.query_count', 0)
            request.environ['altair.queryprofile.query_count'] = count + 1


class QueryCountTween(object):
    def __init__(self, handler, registry):
        self.handler = handler
        self.registry = registry

    def __call__(self, request):
        try:
            request.environ['altair.queryprofile.query_count'] = 0
            return self.handler(request)
        finally:
            count = request.environ.get('altair.queryprofile.query_count', -1)
            if count > -1:
                url = request.url
                logger.debug('*' * 80 + '\n' + 'query count during {url}: {count}'.format(url=url, count=count))
