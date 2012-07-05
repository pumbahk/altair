# coding: utf-8
from altaircms.lib.fanstatic_decorator import with_fanstatic_jqueries
from pyramid.view import view_config, view_defaults
from altaircms.auth.api import require_login
from . import forms

@view_config(route_name='topicdemo', renderer='altaircms.plugins.widget.topic.app:templates/topicdemo.mako',
             permission='page_create', request_method="GET", decorator=with_fanstatic_jqueries)
def topicdemo(request):
    return {}

@view_config(route_name='topicdialog', renderer='altaircms.plugins.widget.topic.app:templates/topicdialog.mako',
             permission='page_create', request_method="GET", decorator=with_fanstatic_jqueries)
def topicdialog(request):
    form = forms.TopicChoiceForm()
    return {"form": form}
