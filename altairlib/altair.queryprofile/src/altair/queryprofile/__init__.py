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
from pyramid_dogpile_cache import get_region

logger = logging.getLogger(__name__)

REGION_NAME = 'altair_queryprofile'

def includeme(config):
    config.include('pyramid_dogpile_cache')
    config.add_tween('altair.queryprofile.tween_factory')


@event.listens_for(Engine, "before_cursor_execute")
def _before_cursor_execute(conn, cursor, stmt, params, context, execmany):
    setattr(conn, 'pdtb_start_timer', time.time())

@event.listens_for(Engine, "after_cursor_execute")
def _after_cursor_execute(conn, cursor, stmt, params, context, execmany):
    request = get_current_request()
    stop_timer = time.time()
    if request is not None:
        engines = request.environ.get('altair.queryprofile.engines', {})
        conn_url = conn.engine.url
        if conn_url not in engines:
            engines[conn_url] = len(engines)
        statements = request.environ.get('altair.queryprofile.statements', {})
        stmt_list = statements.get(conn_url, [])
        duration = (stop_timer - conn.pdtb_start_timer)
        statements[conn_url] = stmt_list + [{'duration':duration,
                                              'statement': str(stmt)}]
        request.environ['altair.queryprofile.engines'] = engines
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
            for engine_id, statements in self.get_statements(request).items():
                count = len(statements)
                if count >= 0:
                    url = request.url
                    logger.debug('query count during {url}: [{engine_id}] {count}'.format(url=url, engine_id=engine_id, count=count))

    def get_statements(self, request):
        return request.environ.get('altair.queryprofile.statements', {})

    def get_engines(self, request):
        return request.environ.get('altair.queryprofile.engines', {})

class SummarizableQueryCountTween(QueryCountTween):
    fanstatic_config = {}

    def __init__(self, summary_path, handler, registry):
        super(SummarizableQueryCountTween, self).__init__(handler, registry)
        self.summary_path = '/' + summary_path.strip('/')

    def __call__(self, request):
        logger.debug(request.path)
        reg = get_region(REGION_NAME)
        if request.path.startswith(self.summary_path):
            path_info = request.path[len(self.summary_path):].rstrip("/")
            if path_info == "":
                needed = fanstatic.init_needed(script_name=request.environ.get('SCRIPT_NAME'), base_url=self.summary_path, **self.fanstatic_config)
                js.bootstrap.bootstrap.need()
                engines = reg.get('altair.queryprofile.engines')
                if not engines:
                    engines = {}
                queries = reg.get('altair.queryprofile.queries')
                if not queries:
                    queries = {}
                request.response.text = render('altair.queryprofile:templates/summary.mako', dict(queries=queries, engines=engines))
                if needed.has_resources():
                    request.response.body = needed.render_topbottom_into_html(request.response.body)
                return request.response
            else:
                return request.get_response(fanstatic.Fanstatic(lambda environ, start_resp: [], base_url=self.summary_path, **self.fanstatic_config))
        else:
            try:
                return super(SummarizableQueryCountTween, self).__call__(request)
            finally:
                reg.set('altair.queryprofile.engines', self.get_engines(request))
                store_summary(reg, request, self.get_statements(request))

            
def store_summary(reg, request, statements):
    count = sum(len(stmts) for stmts in statements.values())
    queries = reg.get('altair.queryprofile.queries')
    if not queries:
        queries = {}

    route = request.matched_route
    if route is None:
        route_name = request.path
    else:
        route_name = route.name

    summary = queries.get(route_name, {})
    summary['max'] = max(summary.get('max', count), count)
    summary['min'] = min(summary.get('min', count), count)
    if summary['max'] == count:
        summary['statements'] = statements
    queries[route_name] = summary
    reg.set('altair.queryprofile.queries', queries)
