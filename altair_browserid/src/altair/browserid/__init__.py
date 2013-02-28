# This package may contain traces of nuts
from webob.dec import wsgify

class BrowserIDMiddleware(object):
    def __init__(self, app,
                 cookie_name='browserid',
                 env_key='repoze.browserid', # BBB
                 ):
        self.app = app
        self.cookie_name = cookie_name
        self.env_key = env_key

    @wsgify
    def __call__(self, request):
        cookies = request.cookies

        browser_id = cookies.get(self.cookie_name)
        request.environ[self.env_key] = browser_id

        return request.get_response(self.app)
