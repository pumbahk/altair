import hashlib
import hmac

from altair.app.ticketing.cooperation.rakuten_live.models import RakutenLiveSession


def get_r_live_session(request):
    session_key = request.registry.settings.get('r-live.session_key')
    return request.session.get(session_key, None)


def pop_r_live_session(request):
    session_key = request.registry.settings.get('r-live.session_key')
    return request.session.pop(session_key, None)


def has_r_live_session(request):
    """Check if there is the session key having R-Live request parameters."""
    return type(get_r_live_session(request)) is RakutenLiveSession


def is_r_live_referer(request):
    r_live_referer = request.registry.settings.get('r-live.referer')
    return request.referer and request.referer.startswith(r_live_referer)


def validate_authorization_header(request):
    api_key = request.registry.settings.get('r-live.api_key')
    api_secret = request.registry.settings.get('r-live.api_secret')
    return request.headers.get('Authorization') == generate_auth_header_value(api_key, api_secret)


def generate_auth_header_value(api_key, api_secret):
    hasher = hmac.new(api_key, api_secret, digestmod=hashlib.sha256)
    return 'LIVE {}'.format(hasher.hexdigest())
