# -*- coding: utf-8 -*-

from pyramid.config import Configurator

from sqlalchemy import engine_from_config
from altair.sqla import session_scope
import sqlahelper

import logging

from .interfaces import ISejTenant, ISejNWTSUploaderFactory

logger = logging.getLogger(__name__)

def includeme(config):
    from .models import ThinSejTenant
    registry = config.registry
    settings = registry.settings

    default_sej_tenant = ThinSejTenant(
        shop_id=settings.get('altair.sej.shop_id') or settings.get('sej.shop_id'),
        api_key=settings.get('altair.sej.api_key') or settings.get('sej.api_key'),
        inticket_api_url=settings.get('altair.sej.inticket_api_url') or settings.get('sej.inticket_api_url'),
        nwts_endpoint_url=settings.get('altair.sej.nwts.endpoint_url') or settings.get('sej.nwts.url'),
        nwts_terminal_id=settings.get('altair.sej.nwts.terminal_id') or settings.get('sej.terminal_id'),
        nwts_password=settings.get('altair.sej.nwts.password') or settings.get('sej.password'),
        )
    registry.registerUtility(default_sej_tenant, ISejTenant)

    from .nwts import ProxyNWTSUploaderFactory
    nwts_factory = config.maybe_dotted(settings.get('altair.sej.nwts.factory', ProxyNWTSUploaderFactory))
    registry.registerUtility(nwts_factory(registry), ISejNWTSUploaderFactory)

    config.include(configure_session)
    config.include('.communicator')
    config.add_tween('.tweens.sej_dbsession_tween_factory')


def configure_session(config):
    from .models import _session
    from sqlahelper import get_engine
    _session.configure(bind=get_engine())

def setup_routes(config):
    config.add_route('sej.callback'                 , '/callback/')
    config.add_route('sej.callback.form'            , '/callback/form')

def sej_session(func):
    from .models import _session
    return session_scope('sej', _session)(func)

def main(global_config, **local_config):
    settings = dict(global_config)
    settings.update(local_config)

    from sqlalchemy.pool import NullPool
    engine = engine_from_config(settings, poolclass=NullPool)
    sqlahelper.add_engine(engine)

    config = Configurator(settings=settings)
    config.set_root_factory('.resources.TicketingApiResource')
    config.include('altair.app.ticketing.setup_beaker_cache')
    config.include('altair.pyramid_dynamic_renderer')
    config.include('altair.sqlahelper')

    config.include('altair.app.ticketing.payments')
    config.include('altair.app.ticketing.payments.plugins')
    config.include('altair.app.ticketing.cart.setup__renderers')
    config.include('altair.app.ticketing.cart.setup_payment_renderers')
    config.include('altair.app.ticketing.mails')
    config.include('altair.app.ticketing.setup_mailtraverser')
    config.include('altair.app.ticketing.orders.setup_subscribers')
    config.add_tween('.tweens.encoding_converter_tween_factory')
    config.include(setup_routes, "/altair/sej/")

    config.include('.')
    config.scan('.views')

    return config.make_wsgi_app()
