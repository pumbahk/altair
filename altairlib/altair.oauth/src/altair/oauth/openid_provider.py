import json
import base64
from time import mktime
from datetime import timedelta
from dateutil.tz import tzlocal
from .interfaces import IOpenIDProvider
from .exceptions import OpenIDServerError, OpenIDNoSuchIDTokenError, OAuthAccessDeniedError

def encode_jwt(data):
    return base64.b64encode(json.dumps(data, ensure_ascii=False, encoding='utf-8'))

def assume_naive_as_local(dt):
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=tzlocal())
    return dt

def tounixts(dt):
    return mktime(dt.astimezone(tzlocal()).timetuple())

def build_oidconn_basic_jwt_content(issuer, subject, audiences, expiry, issued_at, auth_time, nonce, acr=None, amr=None, azp=None):
    if not isinstance(audiences, basestring):
        if not isinstance(audiences, (list, tuple)):
            audiences = list(audiences)
        if len(audiences) == 1:
            audiences = audiences[0]
    expiry = assume_naive_as_local(expiry)
    issued_at = assume_naive_as_local(issued_at)
    local = tzlocal()
    retval = dict(
        iss=issuer,
        sub=subject[0:256],
        aud=audiences,
        exp=tounixts(expiry),
        iat=tounixts(issued_at)
        )

    if auth_time is not None:
        auth_time = assume_naive_as_local(auth_time)
        retval['auth_time'] = tounixts(auth_time)

    if nonce is not None:
        retval['nonce'] = nonce

    if acr is not None:
        retval['acr'] = acr

    if amr is not None:
        retval['amr'] = amr

    if azp is not None:
        retval['azp'] = azp

    return retval


class OpenIDProvider(object):
    def __init__(self, oauth_provider, id_token_store, issuer, token_expiration_time):
        self.oauth_provider = oauth_provider
        self.id_token_store = id_token_store
        self.issuer = issuer
        self.token_expiration_time = token_expiration_time

    def handle_authentication_request(self, subject_id, nonce=None, max_age=None):
        identity = dict(
            openid_subject_id=subject_id,
            openid_nonce=nonce,
            openid_max_age=max_age
            )
        return identity

    def issue_id_token(self, client_id, identity, acr=None, amr=None, azp=None, additional_audiences=[], token_expiration_time=None, authenticated_at=None, aux={}):
        max_age = identity['openid_max_age']
        expire_at = None
        if max_age is not None:
            if authenticated_at is None:
                raise OpenIDServerError(u'authenticated_at is not provided while max_age is given')
            expire_at = authenticated_at + timedelta(seconds=max_age)
        now = self.oauth_provider.now_getter() 
        issuer = self.issuer
        if callable(issuer):
            issuer = issuer(client_id, identity)
        id_token = encode_jwt(build_oidconn_basic_jwt_content(
            issuer=issuer,
            subject=identity['openid_subject_id'],
            audiences=[client_id] + additional_audiences,
            expiry=now + timedelta(seconds=token_expiration_time or self.token_expiration_time),
            issued_at=now,
            auth_time=authenticated_at,
            nonce=identity['openid_nonce'],
            acr=acr,
            amr=amr,
            azp=azp
            ))
        self.id_token_store[id_token] = dict(
            client_id=client_id,
            identity=identity,
            aux=aux,
            expire_at=expire_at
            )
        return id_token

    def revoke_id_token(self, client_id, id_token):
        authn_descriptor = self.get_authn_descriptor_by_id_token(id_token)
        if authn_descriptor['client_id'] != client_id:
            raise OAuthAccessDeniedError(u'client_id does not match')
        del self.id_token_store[id_token]
        return authn_descriptor

    def get_authn_descriptor_by_id_token(self, id_token):
        try:
            retval = self.id_token_store[id_token]
        except:
            raise OpenIDNoSuchIDTokenError(id_token) 
        now = self.oauth_provider.now_getter()
        if retval['expire_at'] >= now:
            raise OpenIDNoSuchIDTokenError(id_token) 
        return retval
