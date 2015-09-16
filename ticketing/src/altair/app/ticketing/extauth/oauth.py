from urlparse import urlparse

class Client(object):
    authorized_scope = {u'user_info'}

    def validate_redirect_uri(self, redirect_uri):
        try:
            parsed = urlparse(redirect_uri)
        except:
            return False
        if parsed.scheme not in ('http', 'https'):
            return False
        return True

    def validate_secret(self, secret):
        return True


class ClientRepository(object):
    def lookup(self, client_id):
        return Client()

