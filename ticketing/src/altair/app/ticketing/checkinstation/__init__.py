# -*- coding:utf-8 -*-

from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from sqlalchemy.pool import NullPool
import sqlahelper

import logging
logger = logging.getLogger(__name__)

def includeme(config):
    ## ad image
    config.add_static_view('static', 'altair.app.ticketing.checkinstation:static', cache_max_age=3600)
    config.include(".adimagecollector")

    ## sample http://placekitten.com/790/590
    config.add_ad_image(imagespec="altair.app.ticketing.checkinstation:static/ad/sample.jpg")

    ## endpoint
    config.include(".endpointcollector")
    config.add_endpoint_route("login.status", "/login/status")
    config.add_endpoint_route("performance.list", "/performance/list")
    config.add_endpoint_route("qr.ticketdata", "/qr/ticketdata")
    config.add_endpoint_route("qr.ticketdata.collection", "/qr/ticketdata/collection")
    config.add_endpoint_route("qr.svgsource.one", "/qr/svgsource/one")
    config.add_endpoint_route("qr.svgsource.all", "/qr/svgsource/all")
    config.add_endpoint_route("qr.update.printed_at", "/qr/printed/update")
    config.add_endpoint_route("orderno.verified_data", "/orderno/verified_data")

    ## extra url
    config.add_endpoint_extra("image_from_svg", "http://localhost:8000") ##impl xxx
    config.include("altair.exclog")
    config.scan(".views")

"""
/login
/logout
"""

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

    ## svg builder
    config.include('altair.app.ticketing.tickets.setup_svg')
    config.include('altair.app.ticketing.qr', route_prefix='qr')

    config.add_static_view('static', 'altair.app.ticketing.checkinstation:static', cache_max_age=3600)
    config.add_static_view('_static', 'altair.app.ticketing:static', cache_max_age=10800)

    config.include(".")
    return config.make_wsgi_app()
