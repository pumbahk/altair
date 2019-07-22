import hashlib
import hmac


def get_r_live_session(request):
    session_key = request.registry.settings.get('r-live.session_key')
    return request.session.get(session_key, None)


def pop_r_live_session(request):
    session_key = request.registry.settings.get('r-live.session_key')
    return request.session.pop(session_key, None)


def has_r_live_session(request):
    """Check if there is the session key having R-Live request parameters."""
    from altair.app.ticketing.cooperation.rakuten_live.models import RakutenLiveSession
    return type(get_r_live_session(request)) is RakutenLiveSession


def validate_r_live_auth_header(request):
    """Validate if authorization header value."""
    # Authorization header value is set to request.authorization
    # after converted by webob.descriptors#parse_auth if exists
    if not request.authorization:
        return False

    api_key = request.registry.settings.get('r-live.api_key')
    api_secret = request.registry.settings.get('r-live.api_secret')
    live_auth_type = request.registry.settings.get('r-live.auth_type')

    auth_type, hash_val = request.authorization
    return auth_type == live_auth_type and hash_val == generate_r_live_auth_hash(api_key, api_secret)


def generate_r_live_auth_hash(api_key, api_secret):
    hasher = hmac.new(api_key, api_secret, digestmod=hashlib.sha256)
    return hasher.hexdigest()


def convert_type(target, func):
    try:
        return func(target)
    except (TypeError, ValueError):
        return None
