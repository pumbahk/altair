class OAuthError(Exception):
    pass


class OAuthNoSuchAccessTokenError(OAuthError):
    pass


class OAuthBadRequestError(OAuthError):
    pass


class OAuthRenderableError(OAuthError):
    pass


class OAuthUnauthorizedClientError(OAuthRenderableError):
    error_string = u'unauthorized_client'
    http_status = 401


class OAuthAccessDeniedError(OAuthRenderableError):
    error_string = u'access_denied'
    http_status = 403


class OAuthInvalidScopeError(OAuthRenderableError):
    error_string = u'invalid_scope'
    http_status = 400


class OAuthServerError(OAuthRenderableError):
    error_string = u'server_error'
    http_status = 500


class OAuthTemporaryUnavailableError(OAuthRenderableError):
    error_string = u'temporary_unavailable'
    http_status = 503


class OAuthClientNotFound(OAuthUnauthorizedClientError):
    pass


class OAuthInvalidSecretError(OAuthUnauthorizedClientError):
    pass


class OAuthNoSuchAuthorizationCodeError(OAuthUnauthorizedClientError):
    pass
