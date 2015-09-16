from altair.mobile.interfaces import IMobileRequest
from altair.oauth.response import OAuthResponseRenderer

def get_oauth_response_renderer(request):
    if IMobileRequest.providedBy(request):
        encoding = request.io_codec
    else:
        encoding = 'utf-8'
    return OAuthResponseRenderer(encoding)
