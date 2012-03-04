# -*- coding: utf-8 -*-
from pyramid.config import Configurator
from pyramid.renderers import render

from sqlalchemy import engine_from_config

from .models import initialize_sql
from .resources import RootFactory, groupfinder

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

import sqlahelper

try:
    import pymysql_sa
    pymysql_sa.make_default_mysql_dialect()
    print 'Using PyMySQL'
except:
    pass
from deform import Form


def renderer(template, **kwargs):
    return render('_deform/%s.mako' % template, kwargs)

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    initialize_sql(engine)
    sqlahelper.add_engine(engine)

    authn_policy = AuthTktAuthenticationPolicy('secretstring',
                                               callback=groupfinder)
    authz_policy = ACLAuthorizationPolicy()

    config = Configurator(settings=settings,
                          root_factory='ticketing.resources.RootFactory',
                          authentication_policy=authn_policy,
                          authorization_policy=authz_policy)

    Form.set_default_renderer(renderer)

    config.add_static_view('static', 'ticketing:static', cache_max_age=3600)
    config.add_static_view('_deform', 'deform:static', cache_max_age=3600)

    config.add_view('pyramid.view.append_slash_notfound_view',
                    context='pyramid.httpexceptions.HTTPNotFound')
    
    config.include('ticketing.views.add_routes' , route_prefix='/')
    
    config.add_renderer('.html', 'pyramid.mako_templating.renderer_factory')

    config.scan('ticketing')

    return config.make_wsgi_app()
