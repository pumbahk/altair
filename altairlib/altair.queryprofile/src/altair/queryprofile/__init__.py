# -*- coding:utf-8 -*-
import time
import threading
import logging
from pyramid.threadlocal import get_current_request
from pyramid.renderers import render
from sqlalchemy import event
from sqlalchemy.engine.base import Engine
from zope.interface import Interface, Attribute, implementer
import fanstatic
import js.bootstrap

logger = logging.getLogger(__name__)
lock = threading.Lock()

def includeme(config):
    config.add_tween('altair.queryprofile.tween_factory')
    config.registry.registerUtility(QuerySummarizer())


def get_summarizer(request):
    return request.registry.queryUtility(IQuerySummarizer)

@event.listens_for(Engine, "before_cursor_execute")
def _before_cursor_execute(conn, cursor, stmt, params, context, execmany):
    setattr(conn, 'pdtb_start_timer', time.time())

@event.listens_for(Engine, "after_cursor_execute")
def _after_cursor_execute(conn, cursor, stmt, params, context, execmany):
    request = get_current_request()
    stop_timer = time.time()
    if request is not None:
        with lock:
            engine_id = id(conn.engine)
            engines = request.registry.setdefault('altair.queryprofile.engines', {})
            engine = engines.get(engine_id)
            if engine is None:
                i = len(engines)
                engines[engine_id] = (i, str(conn.engine))
            statements = request.environ.get('altair.queryprofile.statements', {})
            stmt_list = statements.get(engine_id, [])
            duration = (stop_timer - conn.pdtb_start_timer)
            statements[engine_id] = stmt_list + [{'duration':duration,
                                                  'statement': str(stmt)}]
            request.environ['altair.queryprofile.statements'] = statements


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
            return self.handler(request)
        finally:
            for engine_id, count in self.get_counts(request):

                if count > -1:
                    url = request.url
                    logger.debug('query count during {url}: {count}'.format(url=url, count=count))

    def get_counts(self, request):
        for engine_id, statements in request.environ.get('altair.queryprofile.statements', {}).items():
            yield engine_id, len(statements)


class SummarizableQueryCountTween(QueryCountTween):
    fanstatic_config = {}

    def __init__(self, summary_path, handler, registry):
        super(SummarizableQueryCountTween, self).__init__(handler, registry)
        self.summary_path = '/' + summary_path.strip('/')

    def __call__(self, request):
        logger.debug(request.path)
        if request.path.startswith(self.summary_path):
            path_info = request.path[len(self.summary_path):].rstrip("/")
            if path_info == "":
                needed = fanstatic.init_needed(script_name=request.environ.get('SCRIPT_NAME'), base_url=self.summary_path, **self.fanstatic_config)
                js.bootstrap.bootstrap.need()
                summarizer = get_summarizer(request)
                engines = request.registry.get('altair.queryprofile.engines', {})
                request.response.text = render('altair.queryprofile:templates/summary.mako',
                                               dict(summarizer=summarizer,
                                                    engines=engines))
                if needed.has_resources():
                    request.response.body = needed.render_topbottom_into_html(request.response.body)
                return request.response
            else:
                return request.get_response(fanstatic.Fanstatic(lambda environ, start_resp: [], base_url=self.summary_path, **self.fanstatic_config))
        else:
            try:
                return super(SummarizableQueryCountTween, self).__call__(request)
            finally:
                for engine_id, count in self.get_counts(request):
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
        if summary['max'] == count:
            statements = request.environ.get('altair.queryprofile.statements', {})
            summary['statements'] = statements
        self.queries[route_name] = summary
