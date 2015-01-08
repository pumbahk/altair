# -*- coding:utf-8 -*-

""" マルチ決済モジュール
"""

import logging
import functools
import warnings
from zope.interface import implementer
from pyramid.config import ConfigurationError
from pyramid.settings import asbool
from altair.sqla import DBSessionContext, session_scope
from .interfaces import (
    ICardBrandDetecter,
    IMulticheckoutSettingFactory,
    IMulticheckoutSettingListFactory,
    IMulticheckoutImplFactory,
    IMulticheckoutOrderNoDecorator,
)

logger = logging.getLogger(__name__)

def multicheckout_session(func):
    from .models import _session
    return session_scope('multicheckout', _session)(func)

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


@implementer(IMulticheckoutOrderNoDecorator)
class IdentityDecorator(object):
    def decorate(self, order_no):
        return order_no

    def undecorate(self, order_no):
        return order_no


@implementer(IMulticheckoutOrderNoDecorator)
class TestModeDecorator(object):
    def decorate(self, order_no):
        return order_no + "00"

    def undecorate(self, order_no):
        assert order_no.endswith("00")
        return order_no[:-2]


def setup_private_db_session(config):
    from sqlalchemy import engine_from_config
    from sqlalchemy.pool import NullPool
    from .models import _session
    from sqlahelper import get_engine
    _session.remove()
    _session.configure(bind=get_engine())
    config.add_tween(".multicheckout_dbsession_tween")


def setup_components(config):
    reg = config.registry
    reg.registerUtility(config.maybe_dotted(".util.detect_card_brand"), 
                        ICardBrandDetecter)
    reg.registerUtility(MulticheckoutImplFactory(config), IMulticheckoutImplFactory)

    settings = reg.settings


    order_no_decorator = settings.get('altair.multicheckout.order_no_decorator')
    if order_no_decorator is not None:
        order_no_decorator = config.maybe_dotted(order_no_decorator)

    if order_no_decorator is None:
        testing = settings.get('altair.multicheckout.testing', None)
        if testing is None:
            testing = settings.get('multicheckout.testing', None)
            if testing is not None:
                logger.warning('using deprecated setting "multicheckout.testing"')
            else:
                testing = False

        testing = asbool(testing)

        if testing:
            order_no_decorator = TestModeDecorator()
            logger.info('altair.multicheckout operates in testing mode')
        else:
            logger.info('altair.multicheckout operates in normal mode')
            order_no_decorator = IdentityDecorator()
    else:
        logger.info('altair.multicheckout operates with the custom implementation of IMulticheckoutOrderNoDecorator: %s' % order_no_decorator)

    if order_no_decorator is None:
        raise ConfigurationError('no implementation of IMulticheckoutOrderNoDecorator is available')

    reg.registerUtility(order_no_decorator, IMulticheckoutOrderNoDecorator)

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
