# coding: utf-8
from altaircms.lib.fanstatic_decorator import with_fanstatic_jqueries
from pyramid.view import view_config, view_defaults
from altaircms.auth.api import require_login
from . import forms

@view_config(route_name='topcontentdemo', renderer='altaircms.plugins.widget.topcontent.app:templates/topcontentdemo.html',
             permission='page_create', request_method="GET", decorator=with_fanstatic_jqueries)
def topcontentdemo(request):
    return {}

@view_config(route_name='topcontentdialog', renderer='altaircms.plugins.widget.topcontent.app:templates/topcontentdialog.html',
             permission='page_create', request_method="GET", decorator=with_fanstatic_jqueries)
def topcontentdialog(request):
    form = forms.TopcontentChoiceForm()
    return {"form": form}
