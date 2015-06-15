# -*- coding: utf-8 -*-
import re
import json
import transaction
from sqlalchemy import engine_from_config
from pyramid.config import Configurator
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid_beaker import session_factory_from_settings
from pyramid.tweens import EXCVIEW
from pyramid.interfaces import IDict

import sqlahelper

authn_exemption = re.compile(r'^(/_deform)|(/static)|(/_debug_toolbar)|(/favicon.ico)')


def install_ld():
    from sqlalchemy import orm
    import altair.logicaldeleting
    from altair.samarker.orm import SessionFactoryFactory
    from zope.sqlalchemy import ZopeTransactionExtension
    if altair.logicaldeleting.installed:
        return
    engine = None
    try:
        engine = sqlahelper.get_engine()
    except RuntimeError:
        pass
    session = sqlahelper.get_session()
    assert session is not None
    if session is not None:
        session.remove()
    session_factory = orm.sessionmaker(
        class_=SessionFactoryFactory(altair.logicaldeleting.LogicalDeletableSession),
        extension=ZopeTransactionExtension(),
        query_cls=altair.logicaldeleting.LogicalDeletableQuery
        )
    session.session_factory = session.registry.createfunc = session_factory
    base = sqlahelper.get_base()
    if engine is not None:
        session.configure(bind=engine)
        base.metadata.bind = engine
    altair.logicaldeleting.installed = True

def uninstall_ld():
    import altair.logicaldeleting
    engine = None
    try:
        engine = sqlahelper.get_engine()
    except RuntimeError:
        pass
    prev_base = sqlahelper.get_base()
    prev_session = sqlahelper.get_session()
    prev_session.remove()
    sqlahelper.reset()
    new_session_factory = sqlahelper._session.session_factory
    sqlahelper._session.remove()
    prev_session.session_factory = prev_session.registry.createfunc = new_session_factory
    sqlahelper._session = prev_session
    sqlahelper._base = prev_base
    altair.logicaldeleting.installed = False

install_ld()

def setup_mailtraverser(config):
    from altair.app.ticketing.mails.traverser import EmailInfoTraverser
    reg = config.registry
    traverser = EmailInfoTraverser()
    reg.registerUtility(traverser, name="lots")

def newRootFactory(klass):
    from .resources import ExemptionResource
    def root_factory(request): 
        if authn_exemption.match(request.path):
            return ExemptionResource()
        else:
            return klass(request)
    return root_factory

def exclude_js(path):
    return path.endswith(".js")

def no_exclude(path):
    return False

def register_globals(event):
    from .helpers import Namespace as Namespace_HH
    from .loyalty import helpers as lh
    from altair.viewhelpers import Namespace as Namespace_vh
    event.update(
        HH=Namespace_HH(event['request']),
        lh=lh,
        vh=Namespace_vh(event['request'])
        )

def setup_beaker_cache(config):
    from pyramid_beaker import set_cache_regions_from_settings
    set_cache_regions_from_settings(config.registry.settings)

def main(global_config, **local_config):
    """ This function returns a Pyramid WSGI application.
    """

    with transaction.manager:
        settings = dict(global_config)
        settings.update(local_config)
    
        from .resources import TicketingAdminResource
        from .authentication import CombinedAuthenticationPolicy, APIAuthenticationPolicy
        from .authentication.config import authentication_policy_factory
        from .authentication.apikey.impl import newDBAPIKeyEntryResolver
        from sqlalchemy.pool import NullPool

        engine = engine_from_config(settings, poolclass=NullPool, isolation_level='READ COMMITTED')
        sqlahelper.add_engine(engine)
        
        config = Configurator(settings=settings,
                              root_factory=newRootFactory(TicketingAdminResource)
                              )
    
        config.add_static_view('static', 'altair.app.ticketing:static', cache_max_age=3600)
 
        config.add_view('pyramid.view.append_slash_notfound_view',
                        context='pyramid.httpexceptions.HTTPNotFound')
   
        config.include(setup_beaker_cache)
        config.include("pyramid_fanstatic")

        config.include('pyramid_mako')
        config.add_mako_renderer('.html')
        config.add_mako_renderer('.txt')
    
        config.add_route("index", "/")
   
        config.include('altair.httpsession.pyramid')
        config.include('altair.browserid')
        config.include('altair.exclog')
        config.include('altair.mobile')
        config.include('altair.sqlahelper')
        config.include('altair.now')
        config.include('altair.mq')
        config.include('altair.auth.config')
        config.include('altair.auth:register_plugin_registry')
        config.include('altair.pyramid_dynamic_renderer')

        ### s3 assets
        config.include('altair.pyramid_assets')
        config.include('altair.pyramid_boto')
        config.include('altair.pyramid_boto.s3.assets')
        config.include('altair.pyramid_tz')

        config.include('altair.app.ticketing.core')
        config.include('altair.app.ticketing.mails')
        config.include('altair.app.ticketing.authentication')
        config.include('altair.app.ticketing.multicheckout')
        config.include('altair.app.ticketing.checkout')
        config.include('altair.app.ticketing.sej')
        config.include('altair.app.ticketing.famiport')
        config.include('altair.app.ticketing.sej.userside_impl')
        config.include('altair.app.ticketing.operators' , route_prefix='/operators')
        config.include('altair.app.ticketing.login' , route_prefix='/login')
        config.include('altair.app.ticketing.organizations' , route_prefix='/organizations')
        config.include('altair.app.ticketing.api' , route_prefix='/api')
        config.include('altair.app.ticketing.events' , route_prefix='/events')
        config.include('altair.app.ticketing.orders' , route_prefix='/orders')
        config.include('altair.app.ticketing.master' , route_prefix='/master')
        config.include('altair.app.ticketing.tickets' , route_prefix='/tickets')
        config.include('altair.app.ticketing.products' , route_prefix='/products')
        config.include('altair.app.ticketing.mailmags' , route_prefix='/mailmags')
        config.include('altair.app.ticketing.venues' , route_prefix='/venues')
        config.include('altair.app.ticketing.cooperation', route_prefix='/cooperation')
        config.include('altair.app.ticketing.dashboard' , route_prefix='/dashboard')
        config.include('altair.app.ticketing.accounts' , route_prefix='/accounts')
        config.include('altair.app.ticketing.payment_methods' , route_prefix='/payment_methods')
        config.include('altair.app.ticketing.delivery_methods' , route_prefix='/delivery_methods')
        config.include('altair.app.ticketing.service_fee_methods' , route_prefix='/service_fee_methods')
        config.include('altair.app.ticketing.print_progress')
        config.include('altair.app.ticketing.qr')
        config.include('altair.app.ticketing.members', route_prefix='/members')
        config.include('altair.app.ticketing.memberships', route_prefix='/memberships')
        config.include('altair.app.ticketing.loyalty', route_prefix='/loyalty')
        config.include('altair.app.ticketing.payments')
        config.include('altair.app.ticketing.payments.plugins')
        config.include('altair.app.ticketing.pkginfo')
        config.include('altair.app.ticketing.lots_admin')
        config.include('altair.app.ticketing.admin')

        config.include('altair.app.ticketing.carturl')
        config.include('altair.app.ticketing.description')

        config.include('altair.app.ticketing.permissions.utils.setup_role_and_permissions')

        ## auth plugins
        config.include('altair.rakuten_auth.openid')
        config.include('altair.app.ticketing.fc_auth:register_auth_plugin')
        config.include('altair.app.ticketing.project_specific.nogizaka46.auth')

        ## TBA
        config.add_route("qr.make", "___________") ##xxx:
        config.include('altair.app.ticketing.cart.import_mail_module')
        config.include('altair.app.ticketing.cart.setup_mq')
        config.include('altair.app.ticketing.cart.setup_payment_renderers')
        config.include('.renderers')

        config.scan('altair.app.ticketing.cart.workers')
        config.include('altair.app.ticketing.famiport.userside_workers')
        config.scan('altair.app.ticketing.famiport.userside_workers')
    
        config.add_tween('.tweens.session_cleaner_factory', over=EXCVIEW)

        ## cmsとの通信
        from .api.impl import CMSCommunicationApi
        event_push_communication = CMSCommunicationApi(
            settings["altair.cms.api_url"], 
            settings["altair.cms.api_key"]
            )
        event_push_communication.bind_instance(config)

        config.add_subscriber(register_globals, 'pyramid.events.BeforeRender')

        config.scan(".views")
        config.scan(".response")
   
        config.set_authentication_policy(
            CombinedAuthenticationPolicy([
                authentication_policy_factory(
                    config,
                    'altair.ticketing.admin.authentication.policy'
                    ),
                APIAuthenticationPolicy(
                    resolver_factory=newDBAPIKeyEntryResolver,
                    header_name='X-Altair-Authorization',
                    userid_prefix='__altair_ticketing__api__',
                    principals=['api'])
                ])
            )
        config.set_authorization_policy(ACLAuthorizationPolicy())
        config.add_challenge_view(
            config.registry.settings.get(
                'altair.ticketing.admin.authentication.challenge_view',
                '.views.default_challenge_view'))

        return config.make_wsgi_app()
