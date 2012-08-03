# -*- coding: utf-8 -*-
from pyramid.config import Configurator

from sqlalchemy import engine_from_config

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from pyramid.tweens import EXCVIEW

import sqlahelper
from .api.impl import bound_communication_api ## cmsとの通信
import logging


import re

authn_exemption = re.compile(r'^(/_deform)|(/static)|(/_debug_toolbar)|(/favicon.ico)')

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    from ticketing.logicaldeleting import install as install_ld
    install_ld()
    from .resources import newRootFactory, groupfinder
    from .authentication import CombinedAuthenticationPolicy, APIAuthenticationPolicy
    from .authentication.apikey.impl import newDBAPIKeyEntryResolver
    engine = engine_from_config(settings, 'sqlalchemy.')
    sqlahelper.add_engine(engine)

    config = Configurator(settings=settings,
                          root_factory=newRootFactory(lambda request:authn_exemption.match(request.path)),
                          session_factory=UnencryptedCookieSessionFactoryConfig('altair'))

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

    config.add_static_view('static', 'ticketing:static', cache_max_age=3600)

    config.add_view('pyramid.view.append_slash_notfound_view',
                    context='pyramid.httpexceptions.HTTPNotFound')

    config.include("pyramid_fanstatic")

    config.add_route("index", "/")

    config.include('ticketing.core')
    config.include('ticketing.multicheckout')
    config.include('ticketing.operators' , route_prefix='/operators')
    config.include('ticketing.login' , route_prefix='/login')
    config.include('ticketing.organizations' , route_prefix='/organizations')
    config.include('ticketing.api' , route_prefix='/api')
    config.include('ticketing.admin' , route_prefix='/admin')
    config.include('ticketing.events' , route_prefix='/events')
    config.include('ticketing.orders' , route_prefix='/orders')
    config.include('ticketing.master' , route_prefix='/master')
    config.include('ticketing.products' , route_prefix='/products')
    config.include('ticketing.users' , route_prefix='/users')
    config.include('ticketing.venues' , route_prefix='/venues')
    config.include('ticketing.dashboard' , route_prefix='/dashboard')
    config.include('ticketing.bookmark' , route_prefix='/bookmark')
    config.include('ticketing.accounts' , route_prefix='/accounts')
    config.include('ticketing.payment_methods' , route_prefix='/payment_methods')
    config.include('ticketing.delivery_methods' , route_prefix='/delivery_methods')

    # 上からscanされてしまうためしかたなく追加。scanをinclude先に移動させて、このincludeを削除する。
    #config.include('ticketing.cart' , route_prefix='/cart')

    config.add_renderer('.html' , 'pyramid.mako_templating.renderer_factory')
    config.add_renderer('json'  , 'ticketing.renderers.json_renderer_factory')
    config.add_renderer('csv'   , 'ticketing.renderers.csv_renderer_factory')

    config.add_tween('.tweens.session_cleaner_factory', over=EXCVIEW)
    #config.scan('ticketing') # Bad Code

    ## cmsとの通信
    bound_communication_api(config, 
                            ".api.impl.CMSCommunicationApi", 
                            config.registry.settings["altaircms.event.notification_url"], 
                            config.registry.settings["altaircms.apikey"]
                            )

    config.scan(".views")


    return config.make_wsgi_app()
