from datetime import datetime

from . import VISIBLE_PERFORMANCE_SESSION_KEY

def set_visible_performance(request):
    request.session[VISIBLE_PERFORMANCE_SESSION_KEY] = str(datetime.now())

def set_invisible_performance(request):
    del request.session[VISIBLE_PERFORMANCE_SESSION_KEY]
