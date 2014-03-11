from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from zope.interface.verify import verifyClass

def use_internal_login(config, secret, cookie_name, auth_callback):
    authorization_policy = ACLAuthorizationPolicy()
    config.set_authorization_policy(authorization_policy)
    authentication_policy = AuthTktAuthenticationPolicy(secret=secret,
                                                        cookie_name=cookie_name,
                                                        callback=auth_callback)
    config.set_authentication_policy(authentication_policy)

def setup_internal_login_api_views(config, factory):
    from .interfaces import IInternalAuthAPIResource
    factory = config.maybe_dotted(factory)
    verifyClass(IInternalAuthAPIResource, factory)

    config.add_route("login", "/login", factory=factory)
    config.add_view("altair.app.ticketing.login.internal.views.login_post_api_view", route_name="login", request_method="POST", renderer="json")
    config.add_route("logout", "/logout", factory=factory)
    config.add_view("altair.app.ticketing.login.internal.views.logout_api_view", route_name="logout", request_method="POST")


def setup_internal_login_views(config, factory, login_html="login.html"):
    from .interfaces import IInternalAuthResource
    factory = config.maybe_dotted(factory)
    verifyClass(IInternalAuthResource, factory)

    config.add_route("login", "/login", factory=factory)
    config.add_view("altair.app.ticketing.login.internal.views.login_view", route_name="login", request_method="GET", renderer=login_html)
    config.add_view("altair.app.ticketing.login.internal.views.login_post_view", route_name="login", request_method="POST", renderer=login_html)
    config.add_route("logout", "/logout", factory=factory)
    config.add_view("altair.app.ticketing.login.internal.views.logout_view", route_name="logout", request_method="POST")

def includeme(config):
    config.add_directive("use_internal_login", use_internal_login)
    config.add_directive("setup_internal_login_views", setup_internal_login_views)
    config.add_directive("setup_internal_login_api_views", setup_internal_login_api_views)
