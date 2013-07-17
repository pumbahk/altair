#-*- coding: utf-8 -*-


"""OAuth 2.0 Base Exceptions"""


class OAuth2Exception(Exception):
    """OAuth 2.0 Base Exception"""
    pass

class AuthorizationException(OAuth2Exception):
    """Authorization exception base class."""
    pass


class MissingRedirectURI(OAuth2Exception):
    """Neither the request nor the client specify a redirect_url."""
    pass


class UnauthenticatedUser(OAuth2Exception):
    """The provided user is not internally authenticated, via
    user.is_authenticated()"""
    pass


class UnvalidatedRequest(OAuth2Exception):
    """The method requested requires a validated request to continue."""
    pass


class InvalidRequest(AuthorizationException):
    """The request is missing a required parameter, includes an
    unsupported parameter or parameter value, or is otherwise
    malformed."""
    error = 'invalid_request'


class InvalidClient(AuthorizationException):
    """Client authentication failed (e.g. unknown client, no
    client credentials included, multiple client credentials
    included, or unsupported credentials type)."""
    error = 'invalid_client'


class UnauthorizedClient(AuthorizationException):
    """The client is not authorized to request an authorization
    code using this method."""
    error = 'unauthorized_client'


class AccessDenied(AuthorizationException):
    """The resource owner or authorization server denied the
    request."""
    error = 'access_denied'


class UnsupportedResponseType(AuthorizationException):
    """The authorization server does not support obtaining an
    authorization code using this method."""
    error = 'unsupported_response_type'


class InvalidScope(AuthorizationException):
    """The requested scope is invalid, unknown, or malformed."""
    error = 'invalid_scope'

class AuthenticationException(OAuth2Exception):
    """Authentication exception base class."""
    pass


class InvalidRequest(AuthenticationException):
    """The request is missing a required parameter, includes an
    unsupported parameter or parameter value, repeats the same
    parameter, uses more than one method for including an access
    token, or is otherwise malformed."""
    error = 'invalid_request'


class InvalidToken(AuthenticationException):
    """The access token provided is expired, revoked, malformed, or
    invalid for other reasons."""
    error = 'invalid_token'


class InsufficientScope(AuthenticationException):
    """The request requires higher privileges than provided by the
    access token."""
    error = 'insufficient_scope'

class UnvalidatedRequest(OAuth2Exception):
    """The method requested requires a validated request to continue."""
    pass
