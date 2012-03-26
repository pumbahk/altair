#-*- coding: utf-8 -*-

from hashlib import sha256
from urlparse import parse_qsl
from simplejson import dumps

from pyramid.response import Response

from .exceptions import *
from .models import TimestampGenerator, AccessToken
from .consts import REALM, AUTHENTICATION_METHOD, MAC, BEARER

class Authenticator(object):

    valid                   = False
    access_token            = None
    auth_type               = None
    auth_value              = None
    error                   = None
    attempted_validation    = False

    def __init__(
            self, 
            scope=None, 
            authentication_method=AUTHENTICATION_METHOD):         
        if authentication_method not in [BEARER, MAC, BEARER | MAC]:
            raise OAuth2Exception("Possible values for authentication_method" 
                " are oauth2app.consts.MAC, oauth2app.consts.BEARER, "
                "oauth2app.consts.MAC | oauth2app.consts.BEARER")
        self.authentication_method = authentication_method
        if scope is None:
            self.authorized_scope = None
        elif isinstance(scope, list):
            self.authorized_scope = set([x.category_name for x in scope])
        else:
            self.authorized_scope = set([scope.category_name])

    def validate(self, request):

        self.request = request
        self.bearer_token = request.params.get('bearer_token')
        if "HTTP_AUTHORIZATION" in self.request.headers:
            auth = self.request.headers["HTTP_AUTHORIZATION"].split()
            self.auth_type = auth[0].lower()
            self.auth_value = " ".join(auth[1:]).strip()
        self.request_hostname = self.request.headers.get("REMOTE_HOST")
        self.request_port = self.request.headers.get("SERVER_PORT")
        try:
            self._validate()
        except AuthenticationException, e:
            self.error = e
            raise e
        self.valid = True

    def _validate(self):
        """Validate the request."""
        # Check for Bearer or Mac authorization
        if self.auth_type in ["bearer", "mac"]:
            self.attempted_validation = True
            if self.auth_type == "bearer":
                self._validate_bearer(self.auth_value)
            elif self.auth_type == "mac":
                self._validate_mac(self.auth_value)
            self.valid = True
        # Check for posted/paramaterized bearer token.
        elif self.bearer_token is not None:
            self.attempted_validation = True
            self._validate_bearer(self.bearer_token)
            self.valid = True
        else:
            raise InvalidRequest("Request authentication failed, no "
                "authentication credentials provided.")
        if self.authorized_scope is not None:
            token_scope = set([x.key for x in self.access_token.scope.all()])
            new_scope = self.authorized_scope - token_scope
            if len(new_scope) > 0:
                raise InsufficientScope(("Access token has insufficient "
                    "scope: %s") % ','.join(self.authorized_scope))
        now = TimestampGenerator()()
        if self.access_token.expire < now:
            raise InvalidToken("Token is expired")

    def _validate_bearer(self, token):
        if not self.authentication_method & BEARER:
            raise InvalidToken("Bearer authentication is not supported.")

        self.access_token = AccessToken.get_by_token(token)
        if self.access_token is None:
            raise InvalidToken("Token doesn't exist")

    def _validate_mac(self, mac_header):
        """Validate MAC authentication. Not implemented."""
        if not self.authentication_method & MAC:
            raise InvalidToken("MAC authentication is not supported.")
        mac_header = parse_qsl(mac_header.replace(",","&").replace('"', ''))
        mac_header = dict([(x[0].strip(), x[1].strip()) for x in mac_header])
        for parameter in ["id", "nonce", "mac"]:
            if "parameter" not in mac_header:
                raise InvalidToken("MAC Authorization header does not contain"
                    " required parameter '%s'" % parameter)
        if "bodyhash" in mac_header:
            bodyhash = mac_header["bodyhash"]
        else:
            bodyhash = ""
        if "ext" in mac_header:
            ext = mac_header["ext"]
        else:
            ext = ""
        if self.request_hostname is None:
            raise InvalidRequest("Request does not contain a hostname.")
        if self.request_port is None:
            raise InvalidRequest("Request does not contain a port.")
        nonce_timestamp, nonce_string = mac_header["nonce"].split(":")
        mac = sha256("\n".join([
            mac_header["nonce"], # The nonce value generated for the request
            self.request.method.upper(), # The HTTP request method 
            "XXX", # The HTTP request-URI
            self.request_hostname, # The hostname included in the HTTP request
            self.request_port, # The port as included in the HTTP request
            bodyhash,
            ext])).hexdigest()
        raise NotImplementedError()


    def _get_user(self):

        if not self.valid:
            raise UnvalidatedRequest("This request is invalid or has not "
                "been validated.")
        return self.access_token.user

    user = property(_get_user)

    def _get_scope(self):

        if not self.valid:
            raise UnvalidatedRequest("This request is invalid or has not "
                "been validated.")
        return self.access_token.scope.all()

    scope = property(_get_scope)

    def _get_client(self):

        if not self.valid:
            raise UnvalidatedRequest("This request is invalid or has not "
                "been validated.")
        return self.access_token.client

    client = property(_get_client)

    def error_response(self,
            content='',
            content_type="text/html"):

        response = Response(
            body=content,
            content_type=content_type)

        if not self.attempted_validation:
            response.headers['WWW-Authenticate'] = 'Bearer realm="%s"' % REALM
            response.status_int = 401
            return response
        else:
            if self.error is not None:
                error = getattr(self.error, "error", "invalid_request")
                error_description = self.error.message
            else:
                error = "invalid_request"
                error_description = "Invalid Request."
            header = [
                'Bearer realm="%s"' % REALM,
                'error="%s"' % error,
                'error_description="%s"' % error_description]
            if isinstance(self.error, InsufficientScope):
                header.append('scope=%s' % ' '.join(self.authorized_scope))
                response.status_int = 403
            elif isinstance(self.error, InvalidToken):
                response.status_int = 401
            elif isinstance(self.error, InvalidRequest):
                response.status_int = 400
            else:
                response.status_int = 401
            response.headers['WWW-Authenticate'] = ', '.join(header)
            return response


class JSONAuthenticator(Authenticator):

    callback = None
    
    def __init__(self, scope=None):
        Authenticator.__init__(self, scope=scope)
        
    def validate(self, request):
        self.callback = request.params.get('callback')
        return Authenticator.validate(self, request)
        
    def response(self, data):

        json_data = dumps(data)
        if self.callback is not None:
            json_data = "%s(%s);" % (self.callback, json_data)
        response = Response(
            content=json_data,
            content_type='application/json')
        return response

    def error_response(self):
        if self.error is not None:
            content = dumps({
                "error":getattr(self.error, "error", "invalid_request"),
                "error_description":self.error.message})
        else:
            content = ({
                "error":"invalid_request",
                "error_description":"Invalid Request."})
        if self.callback is not None:
            content = "%s(%s);" % (self.callback, content)
        response = Authenticator.error_response(
            self,
            content=content,
            content_type='application/json')
        if self.callback is not None:
            response.status_int = 200
        return response
