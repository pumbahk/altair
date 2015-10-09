class OAuthError(Exception):
    pass


class OAuthNoSuchAccessTokenError(OAuthError):
    pass


class OAuthRenderableError(OAuthError):
    pass


class OAuthBadRequestError(OAuthRenderableError):
    error_string = 'invalid_request'
    http_status = 400


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

class OpenIDServerError(OAuthServerError):
    pass

class OpenIDNoSuchIDTokenError(OAuthRenderableError):
    error_string = u'id_token_not_found'
    http_status = 404

class OpenIDLoginRequired(OAuthRenderableError):
    error_string = u'login_required'
    http_status = 412

class OpenIDConsentRequired(OAuthRenderableError):
    error_string = u'consent_required'
    http_status = 412

class OpenIDAccountSelectionRequired(OAuthRenderableError):
    error_string = u'account_selection_required'
    http_status = 412

