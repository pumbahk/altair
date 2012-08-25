import logging
from pyramid.threadlocal import get_current_request

class BrowserIdHandler(logging.StreamHandler):
    def __init__(self, *args, **kwargs):
        super(BrowserIdHandler, self).__init__(*args, **kwargs)
        self.addFilter(BrowserIdFilter())

class BrowserIdFilter(logging.Filter):
    def filter(self, record):
        record.browserid = None
        record.url = None
        request = get_current_request()
        if request is None:
            return True

        record.browserid = request.environ.get('repoze.browserid')
        record.url = request.url
        return True
