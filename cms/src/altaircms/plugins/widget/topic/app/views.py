# coding: utf-8
from altaircms.fanstatic import with_fanstatic_jqueries
from pyramid.view import view_config

@view_config(route_name='topicdemo', renderer='altaircms.plugins.widget.topic.app:templates/topicdemo.mako',
             permission='page_create', request_method="GET", decorator=with_fanstatic_jqueries)
def topicdemo(request):
    return {}
