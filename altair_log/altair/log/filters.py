import logging
import fluent.handler
from pyramid.threadlocal import get_current_request

class BrowserIdStreamHandler(logging.StreamHandler):
    def __init__(self, *args, **kwargs):
        super(BrowserIdStreamHandler, self).__init__(*args, **kwargs)
        self.addFilter(BrowserIdFilter())

BrowserIdHandler = BrowserIdStreamHandler

class BrowserIdFluentHandler(fluent.handler.FluentHandler):
    def __init__(self, *args, **kwargs):
        super(BrowserIdFluentHandler, self).__init__(*args, **kwargs)
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
