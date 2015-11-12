# encoding: utf-8
import logging
from datetime import datetime
from pyramid.config import Configurator
from pyramid.authentication import SessionAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.httpexceptions import HTTPFound

logger = logging.getLogger(__name__)
    
def auth_callback(operator_id, request):
    from .api import lookup_operator_by_id
    user = lookup_operator_by_id(request, operator_id)
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

def get_operator(request):
    from .api import lookup_operator_by_id
    return lookup_operator_by_id(request, request.authenticated_userid)

def main(global_config, **local_config):
    settings = dict(global_config)
    settings.update(local_config)
    settings['mako.directories'] = '%s:templates' % __name__

    config = Configurator(
        settings=settings,
        root_factory='.resources.BaseResource'
        )
    config.set_authentication_policy(SessionAuthenticationPolicy(callback=auth_callback))
    config.set_authorization_policy(ACLAuthorizationPolicy())
    config.add_subscriber(register_template_globals, 'pyramid.events.BeforeRender')
    config.include('pyramid_mako')
    config.include('pyramid_layout')
    config.include('pyramid_fanstatic')
    config.include('pyramid_dogpile_cache')
    config.include('altair.httpsession.pyramid')
    config.include('altair.browserid')
    config.include('altair.exclog')
    config.include('altair.sqlahelper')
    config.add_static_view('static', '%s:static' % __name__, cache_max_age=3600)

    config.add_route('top',  '/')
    config.add_route('logout',  '/logout')
    config.add_route('login',  '/login')
    config.add_route('members.index', '/members', request_method='GET')
    config.add_route('members.delete', '/members', request_method='POST', request_param='doDelete')
    config.add_route('members.bulk_add', '/members', request_method='POST', request_param='doBulkAdd')
    config.add_route('members.new', '/members/+')
    config.add_route('members.edit', '/members/{id}')
    config.add_route('member_sets.index', '/member_sets', request_method='GET')
    config.add_route('member_sets.delete', '/member_sets', request_method='POST', request_param='doDelete')
    config.add_route('member_sets.new', '/member_sets/+')
    config.add_route('member_sets.edit', '/member_sets/{id}')
    config.add_route('member_kinds.index', '/member_kinds', request_method='GET')
    config.add_route('member_kinds.delete', '/member_kinds', request_method='POST', request_param='doDelete')
    config.add_route('member_kinds.new', '/member_kinds/+')
    config.add_route('member_kinds.edit', '/member_kinds/{id}')
    config.add_route('operators.index', '/operators', request_method='GET')
    config.add_route('operators.delete', '/operators', request_method='POST', request_param='doDelete')
    config.add_route('operators.new', '/operators/+')
    config.add_route('operators.edit', '/operators/{id}')
    config.add_route('oauth_clients.index', '/oauth_clients', request_method='GET')
    config.add_route('oauth_clients.new', '/oauth_clients/+')
    config.add_route('oauth_clients.delete', '/oauth_clients', request_method='POST', request_param='doDelete')
    config.add_route('organizations.edit', '/organizations/{id}/edit', factory='.resources.OrganizationCollectionResource', traverse='/{id}')
    config.scan('.views')
    config.add_request_method(lambda request: datetime.now(), 'now', reify=True)
    config.add_request_method(get_operator, 'operator', reify=True)
    return config.make_wsgi_app()
