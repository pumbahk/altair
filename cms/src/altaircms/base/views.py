# coding: utf-8
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.security import authenticated_userid
from pyramid.view import view_config
from altaircms.fanstatic import bootstrap_need


@view_config(name='client', renderer='altaircms:templates/client/form.mako', permission='view')
def client(request):
    return dict()


@view_config(name='', renderer='altaircms:templates/dashboard.mako', permission='authenticated')
def dashboard(request):
    """
    ログイン後トップページ
    """
    bootstrap_need()
    return dict()
