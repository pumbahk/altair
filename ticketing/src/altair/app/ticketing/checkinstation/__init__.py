# -*- coding:utf-8 -*-

from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from sqlalchemy.pool import NullPool
import sqlahelper

import logging
logger = logging.getLogger(__name__)

def includeme(config):
    config.scan(".views")

def find_group(user_id, request):
    return ["group:sales_counter"]

def main(global_config, **local_config):
    settings = dict(global_config)
    settings.update(local_config)

    engine = engine_from_config(settings, poolclass=NullPool)
    sqlahelper.add_engine(engine)

    config = Configurator(settings=settings, 
                          root_factory=".resources.CheckinStationResource")
    config.add_renderer('.html' , 'pyramid.mako_templating.renderer_factory')
    config.add_renderer('lxml'  , 'altair.app.ticketing.renderers.lxml_renderer_factory')

    ## login/logout
    config.include('altair.app.ticketing.login.internal')
    config.use_internal_login(secret=settings['authtkt.secret'], cookie_name='checkinstation.auth_tkt', auth_callback=find_group)
    config.setup_internal_login_api_views(factory=".resources.CheckinStationResource")
    config.add_forbidden_view("altair.app.ticketing.login.internal.views.login_view", renderer="altair.app.ticketing.checkinstation:templates/login.html")

    config.include('altair.app.ticketing.qr', route_prefix='qr')
    config.include(".")
    config.add_static_view('static', 'altair.app.ticketing.checkinstation:static', cache_max_age=3600)
    config.add_static_view('_static', 'altair.app.ticketing:static', cache_max_age=10800)
    return config.make_wsgi_app()
