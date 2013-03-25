from datetime import datetime, date

session_key = "altair.now.use_datetime"

def get_now(request):
    dt = request.session.get(session_key)
    if dt:
        return dt
    return datetime.now()


def set_now(request, dt):
    if dt is None and session_key in request.session:
        del request.session[session_key]
    else:
        request.session[session_key] = dt


def get_today(request):
    d = get_now(request)
    return date(d.year, d.month, d.day)
