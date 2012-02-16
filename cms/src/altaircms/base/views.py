# coding: utf-8
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.security import authenticated_userid
from pyramid.view import view_config


@view_config(name='client', renderer='altaircms:templates/client/form.mako', permission='view')
def client(request):
    return dict()


@view_config(name='', renderer='altaircms:templates/dashboard.mako', permission='authenticated')
def dashboard(request):
    """
    ログイン後トップページ
    """
    return dict()


class BaseApiView(object):
    """
    APIビューの基底クラス
    """
    def __init__(self, request):
        self.request = request

        func = getattr(self, request.method.lower())
        func()

    def get(self):
        pass

    def post(self):
        pass

    def delete(self):
        pass

    def put(self):
        pass
