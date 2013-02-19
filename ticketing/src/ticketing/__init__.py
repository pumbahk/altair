# -*- coding: utf-8 -*-
from ticketing.logicaldeleting import install as install_ld
install_ld()

import re
import json

from sqlalchemy import engine_from_config
from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid_beaker import session_factory_from_settings
from pyramid.tweens import EXCVIEW
from pyramid.interfaces import IDict

import sqlahelper

authn_exemption = re.compile(r'^(/_deform)|(/static)|(/_debug_toolbar)|(/favicon.ico)')

def main(global_config, **local_config):
    """ This function returns a Pyramid WSGI application.
    """
    settings = dict(global_config)
    settings.update(local_config)

    from .resources import newRootFactory, groupfinder
    from .authentication import CombinedAuthenticationPolicy, APIAuthenticationPolicy
    from .authentication.apikey.impl import newDBAPIKeyEntryResolver
    from sqlalchemy.pool import NullPool

    engine = engine_from_config(settings, poolclass=NullPool)
    sqlahelper.add_engine(engine)

    config = Configurator(settings=settings,
                          root_factory=newRootFactory(lambda request:authn_exemption.match(request.path)),
                          session_factory=session_factory_from_settings(settings))

    config.set_authentication_policy(
        CombinedAuthenticationPolicy([
            AuthTktAuthenticationPolicy(
                'secretstring',
                cookie_name='backendtkt',
                callback=groupfinder),
            APIAuthenticationPolicy(
                resolver_factory=newDBAPIKeyEntryResolver,
                header_name='X-Altair-Authorization',
                userid_prefix='__altair_ticketing__api__',
                principals=['api'])
            ])
        )
    config.set_authorization_policy(ACLAuthorizationPolicy())

    # multicheckout
    domain_candidates = json.loads(config.registry.settings["altair.cart.domain.mapping"])
    config.registry.utilities.register([], IDict, "altair.cart.domain.mapping", domain_candidates)

    config.add_static_view('static', 'ticketing:static', cache_max_age=3600)

    config.add_view('pyramid.view.append_slash_notfound_view',
                    context='pyramid.httpexceptions.HTTPNotFound')

    config.include("pyramid_fanstatic")

    config.add_route("index", "/")

    config.include('ticketing.mobile')
    config.include('ticketing.core')
    config.include('ticketing.multicheckout')
    config.include('ticketing.checkout')
    config.include('ticketing.operators' , route_prefix='/operators')
    config.include('ticketing.login' , route_prefix='/login')
    config.include('ticketing.organizations' , route_prefix='/organizations')
    config.include('ticketing.api' , route_prefix='/api')
    config.include('ticketing.admin' , route_prefix='/admin')
    config.include('ticketing.events' , route_prefix='/events')
    config.include('ticketing.orders' , route_prefix='/orders')
    config.include('ticketing.master' , route_prefix='/master')
    config.include('ticketing.tickets' , route_prefix='/tickets')
    config.include('ticketing.products' , route_prefix='/products')
    config.include('ticketing.mailmags' , route_prefix='/mailmags')
    config.include('ticketing.venues' , route_prefix='/venues')
    config.include('ticketing.dashboard' , route_prefix='/dashboard')
    config.include('ticketing.bookmark' , route_prefix='/bookmark')
    config.include('ticketing.accounts' , route_prefix='/accounts')
    config.include('ticketing.payment_methods' , route_prefix='/payment_methods')
    config.include('ticketing.delivery_methods' , route_prefix='/delivery_methods')
    config.include("ticketing.qr")
    config.include("ticketing.members", route_prefix='/members')
    config.include("ticketing.memberships", route_prefix="/memberships")
    config.include('ticketing.payments')
    config.include('ticketing.payments.plugins')
    config.include('ticketing.pkginfo')
    ## TBA
    config.add_route("qr.make", "___________") ##xxx:
    config.include(config.maybe_dotted("ticketing.cart.import_mail_module"))
    # 上からscanされてしまうためしかたなく追加。scanをinclude先に移動させて、このincludeを削除する。
    #config.include('ticketing.cart' , route_prefix='/cart')

    config.add_renderer('.html' , 'pyramid.mako_templating.renderer_factory')
    config.add_renderer('.txt' , 'pyramid.mako_templating.renderer_factory')
    config.add_renderer('json'  , 'ticketing.renderers.json_renderer_factory')
    config.add_renderer('csv'   , 'ticketing.renderers.csv_renderer_factory')
    config.add_renderer('lxml'  , 'ticketing.renderers.lxml_renderer_factory')

    config.add_tween('.tweens.session_cleaner_factory', over=EXCVIEW)
    #config.scan('ticketing') # Bad Code
    
    ## cmsとの通信
    from .api.impl import CMSCommunicationApi
    event_push_communication = CMSCommunicationApi(
        settings["altaircms.event.notification_url"], 
        settings["altaircms.apikey"]
        )
    event_push_communication.bind_instance(config)
    import ticketing.pyramid_boto
    ticketing.pyramid_boto.register_default_implementations(config)
    import ticketing.assets
    ticketing.assets.register_default_implementations(config)

    config.scan(".views")

    return config.make_wsgi_app()
