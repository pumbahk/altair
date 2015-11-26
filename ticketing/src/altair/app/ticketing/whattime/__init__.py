# -*- coding:utf-8 -*-
from pyramid.tweens import INGRESS
import json
import logging
import sqlahelper
from pyramid.config import Configurator
from pyramid.interfaces import IDict
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
        settings["altair.cms.api_url"], 
        settings["altair.cms.api_key"]
        ).bind_instance(config)


def find_group(user_id, request):
    return ["group:cart_admin"]

def main(global_config, **local_config):
    settings = dict(global_config)
    settings.update(local_config)

    from sqlalchemy.pool import NullPool
    engine = engine_from_config(settings, poolclass=NullPool, isolation_level='READ COMMITTED')
    sqlahelper.add_engine(engine)

    config = Configurator(settings=settings)
    config.include('altair.app.ticketing.setup_beaker_cache')

    config.include('pyramid_mako')
    config.add_mako_renderer('.html')

    config.include("altair.cdnpath")
    config.add_static_view('static', 'altair.app.ticketing.cart:static', cache_max_age=3600)
    config.include('altair.app.ticketing.setup_beaker_cache')

    ### includes altair.*
    config.include('altair.httpsession.pyramid')
    config.include('altair.exclog')
    config.include('altair.browserid')
    config.include('altair.sqlahelper')
    config.include("altair.preview")
    config.include("altair.app.ticketing.carturl")
    config.include('altair.pyramid_dynamic_renderer')

    config.include(install_backend_login)
    config.include(install_cms_accesskey)
    config.include('.')
    config.include('altair.app.ticketing.organization_settings')
    config.include('altair.mobile')
    config.include('altair.app.ticketing.cart.request')
    config.add_tween('altair.app.ticketing.tweens.session_cleaner_factory', under=INGRESS)
    config.add_tween('altair.app.ticketing.cart.tweens.response_time_tween_factory', under=INGRESS)
    return config.make_wsgi_app()

