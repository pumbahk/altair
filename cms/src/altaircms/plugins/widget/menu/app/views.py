# coding: utf-8
from altaircms.lib.fanstatic_decorator import with_fanstatic_jqueries
from pyramid.view import view_config, view_defaults
from altaircms.auth.api import require_login

@view_config(route_name='menudemo', renderer='altaircms.plugins.widget.menu.app:templates/menudemo.mako',
             permission='page_create', request_method="GET", decorator=with_fanstatic_jqueries)
def menudemo(request):
    return {}
