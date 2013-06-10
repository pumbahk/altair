# -*- coding:utf-8 -*-

import threading
import logging
from pyramid.threadlocal import get_current_request
from pyramid.renderers import render
from sqlalchemy import event
from sqlalchemy.engine.base import Engine
from zope.interface import Interface, Attribute, implementer

logger = logging.getLogger(__name__)
lock = threading.Lock()

def includeme(config):
    config.add_tween('altair.queryprofile.tween_factory')
    config.registry.registerUtility(QuerySummarizer())


def get_summarizer(request):
    return request.registry.queryUtility(IQuerySummarizer)

@event.listens_for(Engine, "after_cursor_execute")
def _after_cursor_execute(conn, cursor, stmt, params, context, execmany):
    request = get_current_request()
    if request is not None:
        with lock:
            count = request.environ.get('altair.queryprofile.query_count', 0)
            request.environ['altair.queryprofile.query_count'] = count + 1


def tween_factory(handler, registry):
    summary_path = registry.settings.get('altair.queryprofile.summary_path')
    if summary_path is None:
        return QueryCountTween(handler, registry)
    else:
        return SummarizableQueryCountTween(summary_path, handler, registry)


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

class SummarizableQueryCountTween(QueryCountTween):
    def __init__(self, summary_path, handler, registry):
        super(SummarizableQueryCountTween, self).__init__(handler, registry)
        self.summary_path = summary_path

    def __call__(self, request):
        logger.debug(request.path)
        if request.path.strip('/') == self.summary_path:
            summarizer = get_summarizer(request)
            request.response.text = render('altair.queryprofile:templates/summary.mako',
                                           dict(summarizer=summarizer))
            return request.response

        request.environ['altair.queryprofile.summalize'] = True
        try:
            return super(SummarizableQueryCountTween, self).__call__(request)
        finally:
            count = request.environ['altair.queryprofile.query_count']
            if request.environ.get('altair.queryprofile.summalize'):
                summarizer = get_summarizer(request)
                summarizer(request, count)

            
class IQuerySummarizer(Interface):
    queries = Attribute("summalized queries")

    def __call__(request, count, stmt):
        """ summalize querying """

@implementer(IQuerySummarizer)
class QuerySummarizer(object):
    def __init__(self):
        self.queries = {}

    def __call__(self, request, count):
        route = request.matched_route
        if route is None:
            route_name = request.path
        else:
            route_name = route.name

        summary = self.queries.get(route_name, {})
        summary['max'] = max(summary.get('max', count), count)
        summary['min'] = min(summary.get('min', count), count)
        self.queries[route_name] = summary
