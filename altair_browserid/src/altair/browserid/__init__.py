import logging
from webob.dec import wsgify

logger = logging.getLogger(__name__)

class BrowserIDMiddleware(object):
    def __init__(self, app,
                 cookie_name,
                 env_key,
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

def browserid_filter_factory(global_conf,
                             cookie_name='browserid',
                             env_key='repoze.browserid', # BBB
                             ):
    def filter(app):
        logger.debug('setup altair.browserid')
        return BrowserIDMiddleware(app, cookie_name, env_key)
    return filter
