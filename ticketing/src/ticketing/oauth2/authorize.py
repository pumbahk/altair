#-*- coding: utf-8 -*-

import simplejson as json
from urllib import urlencode
from .consts import ACCESS_TOKEN_EXPIRATION, REFRESHABLE
from .consts import CODE, TOKEN, CODE_AND_TOKEN
from .consts import AUTHENTICATION_METHOD, MAC, BEARER, MAC_KEY_LENGTH
from .exceptions import *
from .lib.uri import add_parameters, add_fragments, normalize

from ticketing.models.boxoffice import *
from ticketing.models import *

import sqlahelper
session = sqlahelper.get_session()

from pyramid.httpexceptions import HTTPFound, HTTPNotFound
import re

absolute_http_url_re = re.compile(r'(?i)^https?://')

RESPONSE_TYPES = {
    "code":CODE,
    "token":TOKEN
}

class Authorizer(object):

    service          = None
    access_ranges   = None
    valid           = False
    error           = None

    def __init__(
            self,
            scope=None,
            authentication_method=AUTHENTICATION_METHOD,
            refreshable=REFRESHABLE,
            response_type=CODE):

        if response_type not in [CODE, TOKEN, CODE_AND_TOKEN]:
            raise OAuth2Exception("Possible values for response_type"
                " are oauth2app.consts.CODE, oauth2app.consts.TOKEN, "
                "oauth2app.consts.CODE_AND_TOKEN")
        self.authorized_response_type = response_type
        self.refreshable = refreshable
        if authentication_method not in [BEARER, MAC]:
            raise OAuth2Exception("Possible values for authentication_method"
                " are oauth2app.consts.MAC and oauth2app.consts.BEARER")
        self.authentication_method = authentication_method
        if scope is None:
            self.authorized_scope = None
        elif isinstance(scope, list):
            self.authorized_scope = set([x.key for x in scope])
        else:
            self.authorized_scope = set([scope.key])

    def __call__(self, request, context):
        try:
            self.validate(request, context)
        except AuthorizationException, e:
            return self.error_redirect()
        return self.grant_redirect()

    def validate(self, request, context):
        params = request.params

        self.response_type  = params.get('response_type')
        self.service_id     = params.get('client_id')
        self.redirect_uri   = params.get('redirect_uri')
        self.scope          = params.get('scope')
        if self.scope is not None:
            self.scope      = set(self.scope.split())
        self.state          = params.get('state')
        self.user           = context.user
        self.request        = request

        try:
            self._validate()
        except AuthorizationException, e:
            self._check_redirect_uri()
            self.error = e
            raise e
        self.valid = True

    def _validate_redirect_uri(self, service):
        if self.redirect_uri is None:
            if service.redirect_uri is None:
                raise MissingRedirectURI("No redirect_uri provided or registered.")
        elif service.redirect_uri is not None:
            if normalize(self.redirect_uri) != normalize(service.redirect_uri):
                self.redirect_uri = service.redirect_uri
                raise InvalidRequest("Registered redirect_uri doesn't match provided redirect_uri.")

    def _validate_response_type(self, response_type, authorized_response_type):
        if response_type is None:
            raise InvalidRequest('response_type is a required parameter.')
        if response_type not in ["code", "token"]:
            raise InvalidRequest("No such response type %s" % response_type)
        if not authorized_response_type & RESPONSE_TYPES.get(self.response_type):
            raise UnauthorizedClient("Response type %s not allowed." % response_type)
        if not absolute_http_url_re.match(self.redirect_uri):
            raise InvalidRequest('Absolute URI required for redirect_uri')

    def _validate(self):
        """Validate the request."""
        if self.service_id is None:
            raise InvalidRequest('No service_id')

        self.service = Service.get_key(self.service_id)
        if not self.service:
            raise InvalidClient("service_id %s doesn't exist" % self.service_id)
        self._validate_redirect_uri(self.service)
        self.redirect_uri = self.redirect_uri or self.service.redirect_uri

        self._validate_response_type(self.response_type, self.authorized_response_type)

        if self.authorized_scope is not None and self.scope is None:
            self.scope = self.authorized_scope
        if self.scope is not None:
            self.access_ranges = Permission.list_in(self.scope)
            access_ranges = set([a.category_name for a in self.access_ranges])
            difference = access_ranges.symmetric_difference(self.scope)
            if len(difference):
                raise InvalidScope("Following access ranges do not "
                    "exist: %s" % ', '.join(difference))
            if self.authorized_scope is not None:
                new_scope = self.scope - self.authorized_scope
                if len(new_scope) > 0:
                    raise InvalidScope("Invalid scope: %s" % ','.join(new_scope))

    def _check_redirect_uri(self):
        if self.redirect_uri is None:
            raise MissingRedirectURI('No redirect_uri to send response.')
        if not absolute_http_url_re.match(self.redirect_uri):
            raise MissingRedirectURI('Absolute redirect_uri required.')

    def error_redirect(self):

        self._check_redirect_uri()
        if self.error is not None:
            e = self.error
        else:
            e = AccessDenied("Access Denied.")
        parameters = {'error': e.error, 'error_description': u'%s' % e.message}
        if self.state is not None:
            parameters['state'] = self.state
        redirect_uri = self.redirect_uri
        if self.authorized_response_type & CODE:
            redirect_uri = add_parameters(redirect_uri, parameters)
        if self.authorized_response_type & TOKEN:
            redirect_uri = add_fragments(redirect_uri, parameters)
        return HTTPFound(location=redirect_uri)

    def _query_string(self):

        if not self.valid:
            raise UnvalidatedRequest("This request is invalid or has not"
                "been validated.")
        parameters = {
            "response_type":self.response_type,
            "service_id":self.service_id}
        if self.redirect_uri is not None:
            parameters["redirect_uri"] = self.redirect_uri
        if self.state is not None:
            parameters["state"] = self.state
        if self.scope is not None:
            parameters["scope"] = ' '.join(self.scope)
        return urlencode(parameters)

    query_string = property(_query_string)

    def grant_redirect(self, headers=None):

        if not self.valid:
            raise UnvalidatedRequest("This request is invalid or has not been validated.")

        if self.user:
            parameters = {}
            fragments = {}
            if self.scope is not None:
                access_ranges = Permission.list_in(self.scope)
            else:
                access_ranges = []

            if RESPONSE_TYPES.get(self.response_type) & TOKEN or \
                    RESPONSE_TYPES.get(self.response_type) & CODE:

                access_token            = AccessToken()
                access_token.operator   = self.user
                access_token.service    = self.service
                access_token.scope      = access_ranges
                add_and_flush(access_token)

                if RESPONSE_TYPES.get(self.response_type) & CODE:
                    parameters['code'] = access_token.key

                if RESPONSE_TYPES.get(self.response_type) & TOKEN:
                    fragments['access_token'] = access_token.token
                    if access_token.refreshable:
                        fragments['refresh_token'] = access_token.refresh_token
                    fragments['expires_in'] = ACCESS_TOKEN_EXPIRATION
                    if self.scope is not None:
                        fragments['scope'] = ' '.join(self.scope)
                    if self.authentication_method == MAC:
                        access_token.mac_key = KeyGenerator(MAC_KEY_LENGTH)()
                        fragments["mac_key"] = access_token.mac_key
                        fragments["mac_algorithm"] = "hmac-sha-256"
                        fragments["token_type"] = "mac"
                    elif self.authentication_method == BEARER:
                        fragments["token_type"] = "bearer"

                merge_and_flush(access_token)

            if self.state is not None:
                parameters['state'] = self.state

            redirect_uri = add_parameters(self.redirect_uri, parameters)
            redirect_uri = add_fragments(redirect_uri, fragments)

            return HTTPFound(location=redirect_uri, headers=headers)
        else:
            raise UnauthenticatedUser("User object associated with the "
                "request is not authenticated.")
