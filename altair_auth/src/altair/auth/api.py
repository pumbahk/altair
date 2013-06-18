from . import REQUEST_KEY

def get_current_request(environ):
    return environ.get(REQUEST_KEY)
