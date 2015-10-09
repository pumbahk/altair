from .exceptions import OAuthRenderableError
from urllib import urlencode
from datetime import datetime

class OAuthResponseRenderer(object):
    def __init__(self, url_encoding):
        self.url_encoding = url_encoding

    def _render_pairs_as_urlencoded_params(self, params):
        return urlencode(
            [
                (
                    k.encode(self.url_encoding),
                    v.encode(self.url_encoding)
                    )
                for k, v in params
                ]
            )


    def _render_exc_as_pairs(self, exc, state=None):
        assert isinstance(exc, OAuthRenderableError)
        params = [
            (u'error', exc.error_string),
            ]
        if state:
            params.append((u'state', state))
        if exc.message:
            params.append((u'error_description', exc.message))
        return params

    def render_exc_as_urlencoded_params(self, exc, state=None):
        params = self._render_exc_as_pairs(exc, state)
        return self._render_pairs_as_urlencoded_params(params)

    def render_exc_as_dict(self, exc, state=None):
        params = self._render_exc_as_pairs(exc, state)
        return dict(params)

    def render_authorization_code_as_urlencoded_params(self, code, state=None):
        params = [
            (u'code', code)
            ]
        if state:
            params.append((u'state', state))
        return self._render_pairs_as_urlencoded_params(params)

    def render_auth_descriptor_as_dict(self, auth_descriptor, aux=None, state=None, now=None):
        if now is None:
            now = datetime.now()
        params = {
            u'access_token': auth_descriptor[u'access_token'],
            u'token_type': auth_descriptor[u'token_type'],
            u'scope': u' '.join(auth_descriptor[u'scope']),
            }
        if auth_descriptor[u'access_token_expire_at'] is not None:
            params[u'expire_in'] = (auth_descriptor[u'access_token_expire_at'] - now).seconds
        if auth_descriptor[u'refresh_token'] is not None:
            params[u'refresh_token'] = auth_descriptor[u'refresh_token']
        if state:
            params[u'state'] = state
        if aux is not None:
            params.update(aux)
        return params
   
    def render_id_token_as_dict(self, id_token):
        return { u'id_token': id_token }

    def render_auth_descriptor_as_urlencoded_params(self, auth_descriptor, state=None, now=None):
        return self._render_pairs_as_urlencoded_params(self.render_auth_descriptor_as_dict(auth_descriptor, state, now).items())
