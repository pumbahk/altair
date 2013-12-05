# -*- coding:utf-8 -*-
from pyramid.tweens import INGRESS
import json
import logging
import sqlahelper
from pyramid.config import Configurator
from pyramid.interfaces import IDict
from pyramid_beaker import session_factory_from_settings
from pyramid_beaker import set_cache_regions_from_settings
from sqlalchemy import engine_from_config
logger = logging.getLogger(__name__)

def includeme(config):
    config.add_route("whattime.nowsetting.form", "/form", factory=".resources.WhattimeAdminResource")
    config.add_route("whattime.nowsetting.set", "/set", factory=".resources.WhattimeAdminResource")
    config.add_route("whattime.nowsetting.goto", "/goto", factory=".resources.WhattimeAdminResource")
    config.scan(".views")

def install_backend_login(config):
    settings = config.registry.settings
    config.include('altair.app.ticketing.login.internal')
    config.use_internal_login(secret=settings['authtkt.secret'], cookie_name='printqr.auth_tkt', auth_callback=find_group)
    config.setup_internal_login_views(factory="altair.app.ticketing.whattime.resources.WhattimeAdminResource", 
                                      login_html="altair.app.ticketing.whattime:templates/login.html")


def install_cms_accesskey(config):
    from .interfaces import IAccessKeyGetter
    from .external import CMSAccessKeyGetter
    settings = config.registry.settings
    cms_accesskey_getter = CMSAccessKeyGetter.from_settings(settings)
    config.registry.registerUtility(cms_accesskey_getter, IAccessKeyGetter, name="cms")
    from altair.app.ticketing.api.impl import CMSCommunicationApi
    CMSCommunicationApi(
        settings["altaircms.event.notification_url"], 
        settings["altaircms.apikey"]
        ).bind_instance(config)


def find_group(user_id, request):
    return ["group:cart_admin"]

def main(global_config, **local_config):
    settings = dict(global_config)
    settings.update(local_config)

    from sqlalchemy.pool import NullPool
    engine = engine_from_config(settings, poolclass=NullPool, isolation_level='READ COMMITTED')
    session_factory = session_factory_from_settings(settings)
    set_cache_regions_from_settings(settings) 
    sqlahelper.add_engine(engine)

    config = Configurator(settings=settings,
                          session_factory=session_factory)
    config.registry['sa.engine'] = engine
    config.add_renderer('.html' , 'pyramid.mako_templating.renderer_factory')
    config.add_renderer('json'  , 'altair.app.ticketing.renderers.json_renderer_factory')
    config.add_renderer('csv'   , 'altair.app.ticketing.renderers.csv_renderer_factory')
    config.include("altair.cdnpath")
    config.add_static_view('static', 'altair.app.ticketing.cart:static', cache_max_age=3600)

    ### includes altair.*
    config.include('altair.exclog')
    config.include('altair.browserid')
    config.include('altair.sqlahelper')
    config.include("altair.preview")
    config.include("altair.app.ticketing.carturl")

    ### selectable renderer
    config.include('altair.app.ticketing.cart.selectable_renderer')

    config.include(install_backend_login)
    config.include(install_cms_accesskey)
    config.include('.')
    config.include('altair.app.ticketing.organization_settings')
    config.include('altair.mobile')
    config.include('altair.app.ticketing.cart.errors')
    config.add_tween('altair.app.ticketing.tweens.session_cleaner_factory', under=INGRESS)
    config.add_tween('altair.app.ticketing.cart.tweens.response_time_tween_factory', under=INGRESS)
    return config.make_wsgi_app()

