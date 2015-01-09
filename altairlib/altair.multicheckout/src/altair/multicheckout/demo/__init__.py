# -*- coding:utf-8 -*-

import logging

logger = logging.getLogger(__name__)

def includeme(config):
    config.add_route('top', '/')
    config.add_route('secure3d_result', '/secure3d_result')
    config.scan()

def setup_session(config):
    from altair.httpsession.pyramid import PyramidSessionFactory
    from altair.mobile.session import http_backend_factory 
    from altair.httpsession.pyramid.interfaces import ISessionHTTPBackendFactory, ISessionPersistenceBackendFactory
    from altair.httpsession.inmemory import factory as inmemory_session_backend_factory
    config.registry.registerUtility(
        lambda request: http_backend_factory(request, 'PHPSESSID', 'secret'),
        ISessionHTTPBackendFactory
        )

    config.registry.registerUtility(
        lambda request: inmemory_session_backend_factory(request),
        ISessionPersistenceBackendFactory
        )
    config.set_session_factory(PyramidSessionFactory())

class DemoMulticheckoutSetting(object):
    def __init__(self, settings):
        self.shop_name = settings['altair.multicheckout.demo.shop_name']
        self.shop_id = settings['altair.multicheckout.demo.shop_id']
        self.auth_id = settings['altair.multicheckout.demo.auth_id']
        self.auth_password = settings['altair.multicheckout.demo.auth_password']

def setup_components(config):
    multicheckout_setting = DemoMulticheckoutSetting(config.registry.settings)
    def get_multicheckout_setting(request, override_name=None, organization_id=None):
        return multicheckout_setting
    config.set_multicheckout_setting_factory(get_multicheckout_setting)

def main():
    return paster_main({})

def paster_main(global_config, **local_config):
    from pyramid.config import Configurator
    import sqlahelper
    from sqlalchemy import engine_from_config
    settings = dict(global_config)
    settings.update(local_config)
    settings['mako.directories'] = __name__ + ':templates'
    engine = engine_from_config(settings, echo=True)
    sqlahelper.add_engine(engine)
    from ..models import Base
    Base.metadata.create_all(engine)
    config = Configurator(settings=settings)
    config.include('pyramid_mako')
    config.include('altair.multicheckout')
    config.include(setup_components)
    config.include(setup_session)
    config.include('.')
    return config.make_wsgi_app()
