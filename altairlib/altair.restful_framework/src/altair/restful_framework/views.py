# -*- coding: utf-8 -*-

from pyramid.httpexceptions import HTTPClientError, HTTPMethodNotAllowed, HTTPForbidden
from pyramid.response import Response

class APIView(object):
    """
    Base fro class-based views. Requests are routed to a view's
    method with the same name as the HTTP method of the requests.
    """

    http_method_name = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace']
    lookup_url_kwargs = None
    permission_classes = []

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)

    @classmethod
    def as_view(cls, **initkwargs):
        def view(request):
            self = cls(**initkwargs)
            self.request = request
            self.lookup_url_kwargs = self.request.matchdict

            return self.dispatch(self.request, **self.lookup_url_kwargs)
        return view

    def initial(self, request, *args, **kwargs):
        """
        Runs anything that needs to occur prior to calling the method handler.
        """
        self.check_permission(request)

    def dispatch(self, request, *args, **kwargs):
        try:
            self.initial(request, *args, **kwargs)

            if request.method.lower() in self.http_method_name:
                handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
            else:
                handler = self.http_method_not_allowed

            response = handler(request, *args, **kwargs)
        except Exception as exc:
            response = self.handle_exception(exc)

        return response

    def handle_exception(self, exc):
        if isinstance(exc, HTTPClientError):
            return exc
        raise exc

    def http_method_not_allowed(self, request, *args, **kwargs):
        raise HTTPMethodNotAllowed

    def get_permissions(self):
        return [permission() for permission in self.permission_classes]

    def check_permission(self, request):
        for permission in self.get_permissions():
            if not permission.has_permission(request, self):
                self.permission_denied(request, message=getattr(permission, 'message', None))

    def check_object_permission(self, request, obj):
        for permission in self.get_permissions():
            if not permission.has_object_permission(request, self, obj):
                self.permission_denied(request, message=getattr(permission, 'message', None))

    def permission_denied(self, request, message):
        raise HTTPForbidden(detail=message)

    def options(self, request, *args, **kwargs):
        response = Response()

        response.headers['Allow'] = ', '.join(self.allow_methods)
        response.headers['Content-Length'] = '0'

        return response

    @property
    def allow_methods(self):
        return [m.upper() for m in self.http_method_name if hasattr(self, m)]
