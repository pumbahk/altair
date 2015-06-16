from datetime import datetime
from pyramid.security import Allow, Deny, Authenticated, DENY_ALL
from pyramid.decorator import reify
from .api import get_client_configuration_registry, get_mmk_sequence

class BaseResource(object):
    __acl__ = [
        (Allow, Authenticated, 'authenticated'),
        (Allow, 'client_code_provided', 'client_code_provided'),
        DENY_ALL,
        ]

    @reify
    def now(self):
        return datetime.now()
    
    def __init__(self, request):
        self.request = request

class FamiPortResource(BaseResource):
    @reify
    def store_code_and_mmk_no(self):
        return self.request.authenticated_userid.partition(':')[::2]

    @property
    def store_code(self):
        return self.store_code_and_mmk_no[0]

    @property
    def mmk_no(self):
        return self.store_code_and_mmk_no[1]

    def gen_serial(self):
        mmk_seq = get_mmk_sequence(self.request) 
        serial = mmk_seq.next_serial(self.now, self.store_code)
        return u'%02d%02d%02d%05d' % (
            self.now.year % 100,
            self.now.month,
            self.now.day,
            serial
            )

class FamiPortServiceResource(FamiPortResource):
    @reify
    def client_code(self):
        return self.request.session['client_code']

    @reify
    def client(self):
        client_configuration_registry = get_client_configuration_registry(self.request)
        return client_configuration_registry.lookup(self.client_code)
