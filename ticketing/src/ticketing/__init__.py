# -*- coding: utf-8 -*-
from pyramid.config import Configurator

from sqlalchemy import engine_from_config
from .resources import RootFactory, groupfinder

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from pyramid.tweens import EXCVIEW

import sqlahelper

import logging


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    sqlahelper.add_engine(engine)

    authn_policy = AuthTktAuthenticationPolicy('secretstring',
        cookie_name='backendtkt',
                                               callback=groupfinder)
    authz_policy = ACLAuthorizationPolicy()

    config = Configurator(settings=settings,
                          root_factory='ticketing.resources.RootFactory',
                          authentication_policy=authn_policy,
                          authorization_policy=authz_policy,
                          session_factory=UnencryptedCookieSessionFactoryConfig('altair'))


    config.add_static_view('static', 'ticketing:static', cache_max_age=3600)

    config.add_view('pyramid.view.append_slash_notfound_view',
                    context='pyramid.httpexceptions.HTTPNotFound')

    config.include("pyramid_fanstatic")

    config.add_route("index", "/")

    config.include('ticketing.core')
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
    config.scan(".views")


    return config.make_wsgi_app()
