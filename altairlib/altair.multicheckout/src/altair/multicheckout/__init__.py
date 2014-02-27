# -*- coding:utf-8 -*-

""" マルチ決済モジュール
"""

import logging
import functools
import warnings
from .interfaces import (
    ICardBrandDetecter,
    IMulticheckoutSettingFactory,
    IMulticheckoutSettingListFactory,
    IMulticheckoutImplFactory,
)
from zope.interface import implementer
from pyramid.config import ConfigurationError

logger = logging.getLogger(__name__)

class DBSessionContext(object):
    def __init__(self, session, name=None):
        self.session = session
        self.name = name

    def __enter__(self):
        pass


    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.name:
            logger.debug('remove {0} dbsession'.format(self.name))
        self.session.remove()

def multicheckout_session(func):
    from .models import _session
    @functools.wraps(func)
    def wrap(*args, **kwargs):
        with DBSessionContext(_session, name="multicheckout"):
            return func(*args, **kwargs)
    return wrap

def multicheckout_dbsession_tween(handler, registry):
    def tween(request):
        from .models import _session
        with DBSessionContext(_session, name="multicheckout"):
            return handler(request)
    return tween
            
@implementer(IMulticheckoutImplFactory)
class MulticheckoutImplFactory(object):
    def __init__(self, config):
        registry = config.registry
        base_url = registry.settings.get('altair.multicheckout.endpoint.base_url')
        if base_url is None:
            base_url = registry.settings.get('altair_checkout3d.base_url')
            if base_url is None:
                raise ConfigurationError("altair.multicheckout.endpoint.base_url is not given")
            else:
                logger.warning("altair.multicheckout.endpoint.base_url is not given; using the value of deprecated altair_checkout3d.base_url setting instead")

        timeout = registry.settings.get('altair.multicheckout.endpoint.timeout')
        if timeout is None:
            timeout = registry.settings.get('altair_checkout3d.timeout')
            if timeout is None:
                raise ConfigurationError("altair.multicheckout.endpoint.timeout is not given")
            else:
                logger.warning("altair.multicheckout.endpoint.timeout is not given; using the value of deprecated altair_checkout3d.timeout setting instead")
        self.base_url = base_url
        self.timeout = timeout

    def __call__(self, request, override_name=None):
        if hasattr(request, 'altair_checkout3d_override_shop_name'):
            if override_name is None:
                warnings.warn(DeprecationWarning('request.altair_checkout3d_override_shop_name is deprecated.'))
                override_name = getattr(request, 'altair_checkout3d_override_shop_name')
            else:
                raise Exception('both override_name and request.altair_checkout3d_override_shop_name are given')
        from . import api
        from .impl import Checkout3D
        setting = api.get_multicheckout_setting(request, override_name=override_name)
        return Checkout3D(
            setting.auth_id,
            setting.auth_password,
            shop_code=setting.shop_id,
            api_base_url=self.base_url,
            api_timeout=self.timeout
            )


def setup_private_db_session(config):
    from sqlalchemy import engine_from_config
    from sqlalchemy.pool import NullPool
    from .models import _session
    engine = engine_from_config(config.registry.settings, poolclass=NullPool)
    _session.remove()
    _session.configure(bind=engine)
    config.add_tween(".multicheckout_dbsession_tween")

def setup_components(config):
    reg = config.registry
    reg.registerUtility(config.maybe_dotted(".util.detect_card_brand"), 
                        ICardBrandDetecter)
    reg.registerUtility(MulticheckoutImplFactory(config), IMulticheckoutImplFactory)

def includeme(config):
    setup_private_db_session(config)
    setup_components(config)
    config.add_directive("set_multicheckout_setting_factory",
                         set_multicheckout_setting_factory)
    config.add_directive("set_multicheckout_setting_list_factory",
                         set_multicheckout_setting_list_factory)


def set_multicheckout_setting_factory(config, factory):
    reg = config.registry
    def register():
        reg.registerUtility(factory, IMulticheckoutSettingFactory)

    intr = config.introspectable(
        category_name="altair.multicheckout.multicheckoutsettings",
        discriminator="altair.multicheckout.multicheckoutsetting",
        title="adapter of Multicheckout Setting",
        type_name="altair.multicheckout.interfaces.IMulticheckoutSetting")

    config.action("altair.multicheckout.multicheckoutsetting",
                  register,
                  introspectables=intr,
                  )

def set_multicheckout_setting_list_factory(config, factory):
    reg = config.registry
    def register():
        reg.registerUtility(factory, IMulticheckoutSettingListFactory)

    intr = config.introspectable(
        category_name="altair.multicheckout.multicheckoutsettings",
        discriminator="altair.multicheckout.multicheckoutsettinglist",
        title="adapter of Multicheckout Setting List",
        type_name="altair.multicheckout.interfaces.IMulticheckoutSetting")

    config.action("altair.multicheckout.multicheckoutsettinglist",
                  register,
                  introspectables=intr,
                  )

def main(global_conf, **settings):
    from sqlalchemy import engine_from_config
    from sqlalchemy.pool import NullPool
    import sqlahelper
    engine = engine_from_config(settings, poolclass=NullPool)
    sqlahelper.add_engine(engine)

    from pyramid.config import Configurator
    from pyramid.session import UnencryptedCookieSessionFactoryConfig
    my_session_factory = UnencryptedCookieSessionFactoryConfig('itsaseekreet')
    config = Configurator(
        settings=settings,
        session_factory=my_session_factory)
    config.include('.')
    config.include('.demo')
    config.include('pyramid_fanstatic')

    return config.make_wsgi_app()
