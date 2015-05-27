from datetime import datetime, date

session_key = "altair.now.use_datetime"
import logging
logger = logging.getLogger("altair.now")

def has_session_key(request):
    return session_key in request.session

def get_now(request):
    dt = request.session.get(session_key)
    if dt is None:
        dt = datetime.now()
    logger.info("get now=%s", dt)
    return dt

def is_now_set(request):
    return request.session.get(session_key) is not None

def set_now(request, dt):
    if dt:
        request.session[session_key] = dt
        logger.info("set now=%s", dt)
    elif dt is None and session_key in request.session:
        logger.info("delete now=%s", dt)
        del request.session[session_key]

def get_today(request):
    d = get_now(request)
    return date(d.year, d.month, d.day)

def includeme(config):
    config.set_request_property(get_now, "now", reify=True)
