# -*- coding:utf-8 -*-
from zope.interface import directlyProvides, noLongerProvides
from .interfaces import (
    IPreviewPermission,
    IPreviewRedirect,
    )
from .api import FORCE_REQUEST_TYPE
from .api import get_force_request_type
from .api import set_preview_request_condition
from altair.mobile.interfaces import (
    IMobileRequest,
    ISmartphoneRequest,
    )

from webob.request import Transcoder

def reset_request_iface(request):
    noLongerProvides(request, IMobileRequest)
    noLongerProvides(request, ISmartphoneRequest)

def preview_tween(handler, registry):
    def tween(request):
        checking = request.registry.queryUtility(IPreviewPermission)
        ## usually, user-access-request cannot preview.
        if not checking.can_preview(request):
            return handler(request)

        set_preview_request_condition(request, True)

        req_type = get_force_request_type(request)
        if req_type == FORCE_REQUEST_TYPE.mobile:
            reset_request_iface(request)
            directlyProvides(request, IMobileRequest)
        elif req_type == FORCE_REQUEST_TYPE.smartphone:
            reset_request_iface(request)
            directlyProvides(request, ISmartphoneRequest)

        response = handler(request)

        if response.content_type is None or response.content_type != 'text/html':
            return response

        permission = checking.has_permission(request)
        redirect = request.registry.queryUtility(IPreviewRedirect)
        if permission:
            return redirect.on_success(request, response, permission)
        else:
            return redirect.on_failure(request, response, permission)           
    return tween
