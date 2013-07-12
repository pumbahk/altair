import logging
import threading
from webob.dec import wsgify

browser = threading.local()
logger = logging.getLogger(__name__)

def get_browserid(request):
    key = request.environ.get('altair.browserid.env_key')
    if key:
        return request.environ.get(key)


def includeme(config):
    config.set_request_property(get_browserid, 'browserid')


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

        browser_id_cookie = cookies.get(self.cookie_name)
        if browser_id_cookie:
            browser_id = str(browser_id_cookie).partition('!')[0]
        else:
            browser_id = None
        browser.id = browser_id
        browser.url = request.url
        request.environ[self.env_key] = browser_id
        request.environ['altair.browserid.env_key'] = self.env_key

        try:
            return request.get_response(self.app)
        finally:
            browser.id = None
            browser.url = None

def browserid_filter_factory(global_conf,
                             cookie_name='browserid',
                             env_key='repoze.browserid', # BBB
                             ):
    def filter(app):
        logger.debug('setup altair.browserid')
        return BrowserIDMiddleware(app, cookie_name, env_key)
    return filter
