# -*- coding:utf-8 -*-

""" マルチ決済モジュール
"""

import logging
import functools
from .interfaces import (
    ICardBrandDetecter,
    IMulticheckoutSettingFactory,
    IMulticheckoutSettingListFactory,
)
from .util import ahead_coms
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
            
def detect_card_brand(request, card_number):
    detecter = request.registry.getUtility(ICardBrandDetecter)
    return detecter(card_number)

def get_card_ahead_com_name(request, code):
    if code in ahead_coms:
        return ahead_coms[code]
    return u"その他"

def includeme(config):
    from sqlalchemy import engine_from_config
    from sqlalchemy.pool import NullPool
    from .models import _session
    engine = engine_from_config(config.registry.settings, poolclass=NullPool,
                                pool_recycle=10)
    _session.remove()
    _session.configure(bind=engine)

    config.add_tween(".multicheckout_dbsession_tween")

    reg = config.registry
    reg.registerUtility(config.maybe_dotted(".util.detect_card_brand"), 
                        ICardBrandDetecter)
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
