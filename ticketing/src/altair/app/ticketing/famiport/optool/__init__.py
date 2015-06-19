from pyramid.config import Configurator
from pyramid.authentication import SessionAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.httpexceptions import HTTPFound
from altair.sqlahelper import from_settings

def auth_callback(user_id, request):
    from .api import lookup_user_by_id
    user = lookup_user_by_id(request, user_id)
    return user and [user.role]

def register_template_globals(event):
    from altair.viewhelpers import Namespace
    from .helpers import Helpers
    class CombinedNamespace(object):
        def __init__(self, namespaces):
            self.namespaces = namespaces

        def __getattr__(self, k):
            for ns in self.namespaces:
                v = getattr(ns, k, None)
                if v is not None:
                    return v
            return object.__getattr__(self, k)

    h = CombinedNamespace([
        Helpers(event['request']),
        Namespace(event['request']),
        ])
    event.update(h=h)


def main(global_conf, **local_conf):
    settings = dict(global_conf)
    settings.update(local_conf)
    settings['mako.directories'] = '%s:templates' % __name__
    config = Configurator(settings=settings)
    config.set_root_factory('.resources.BaseResource')
    config.set_authentication_policy(SessionAuthenticationPolicy(callback=auth_callback))
    config.set_authorization_policy(ACLAuthorizationPolicy())
    config.add_subscriber(register_template_globals, 'pyramid.events.BeforeRender')
    config.include('pyramid_mako')
    config.include('pyramid_fanstatic')
    config.include('altair.httpsession.pyramid')
    config.include('altair.browserid')
    config.include('altair.exclog')
    config.include('altair.sqlahelper')
    config.add_static_view('static', '%s:static' % __name__, cache_max_age=3600)
    config.add_forbidden_view(lambda context, request: HTTPFound(request.route_path('login', _query=dict(return_url=request.path))))
    config.add_route('logout',  '/logout')
    config.add_route('login',  '/login')
    config.add_route('top',  '/', factory='.resources.TopResource')
    config.add_route('example.page_needs_authentication',  '/.example/page_needs_authentication', factory='.resources.ExampleResource')
    config.scan('.views')
    return config.make_wsgi_app()
