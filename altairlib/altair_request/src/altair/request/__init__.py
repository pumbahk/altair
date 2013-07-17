import functools
from webob.cookies import parse_cookie

def includeme(config):
    if hasattr(config, 'add_request_method'):
        set_property = functools.partial(config.add_request_method,
                                         property=True)
    else:
        set_property = config.set_request_property

    set_property(raw_cookies, reify=True)

def raw_cookies(request):
    env = request.environ
    header = env.get('HTTP_COOKIE', '')
    cookies = dict((k, v) for k,v in parse_cookie(header))
    return cookies

