from markupsafe import Markup
from ticketing.cart.helpers import *
from pyramid.threadlocal import get_current_request

def error(names):
    request = get_current_request()
    if not hasattr(request, 'errors'):
        return ''
    if not isinstance(names, list):
        names = [names]
    errs = dict()
    for name in names:
        for err in request.errors.get(name,[]):
            errs[err] = err
    errs = ", ".join(errs.values())
    if request.is_mobile:
        return Markup('<font color="red">%s</font><br />' % errs)
    else:
        return Markup('<p class="error">%s</p>' % errs)
