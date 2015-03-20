from webob.response import Response as WebObResponse

def stringize_resp(request, response):
    if isinstance(response, WebObResponse):
        return WebObResponse.__repr__(response)
    else:
        return repr(response)


