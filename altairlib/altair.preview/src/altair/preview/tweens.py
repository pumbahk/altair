# -*- coding:utf-8 -*-
from zope.interface import directlyProvides
from .interfaces import IPreviewPermission
from .interfaces import IPreviewRedirect
from .api import FORCE_REQUEST_TYPE
from .api import get_force_request_type
from .api import set_preview_request_condition
from altair.mobile.interfaces import IMobileRequest
from altair.mobile.interfaces import ISmartphoneRequest
from altair.mobile.tweens import make_mobile_request

from webob.request import Transcoder

CONTENT_TYPES = ['text/html', 'text/xml', 'application/xhtml+xml']

def _support_mobile_utf8_query_string(request, encoding="cp932"): #xxxx
    coder = Transcoder(encoding)
    try:
        coder.transcode_query(request.query_string)
        request.body = coder.transcode_query(request.body)
    except UnicodeDecodeError:
        coder._trans = lambda b : b.decode("utf-8").encode(encoding)
        request.query_string = coder.transcode_query(request.query_string)
        request.body = coder.transcode_query(request.body)

def _support_mobile_utf8_body(request, encoding="cp932"): #xxxx
    coder = Transcoder(encoding)
    try:
        coder.transcode_query(request.body)
    except UnicodeDecodeError:
        coder._trans = lambda b : b.decode("utf-8").encode(encoding)
        request.body = coder.transcode_query(request.body)

def preview_tween(handler, registry):
    def tween(request):
        checking = request.registry.queryUtility(IPreviewPermission)
        ## usually, user-access-request cannot preview.
        if not checking.can_preview(request):
            return handler(request)
            
        set_preview_request_condition(request, True)

        req_type = get_force_request_type(request)
        if req_type == FORCE_REQUEST_TYPE.mobile and not IMobileRequest.providedBy(request):
            if request.query_string:
                _support_mobile_utf8_query_string(request)
            if request.environ["REQUEST_METHOD"] == "POST":
                _support_mobile_utf8_body(request)
            response = handler(make_mobile_request(request))

        elif req_type == FORCE_REQUEST_TYPE.smartphone and not ISmartphoneRequest.providedBy(request):
            directlyProvides(request, ISmartphoneRequest)
            response = handler(request)
        else:
            response = handler(request)


        if not (response.content_type and
                response.content_type.lower() in CONTENT_TYPES):
            return response

        permission = checking.has_permission(request)
        redirect = request.registry.queryUtility(IPreviewRedirect)
        if permission:
            return redirect.on_success(request, response, permission)
        else:
            return redirect.on_failure(request, response, permission)           
    return tween
