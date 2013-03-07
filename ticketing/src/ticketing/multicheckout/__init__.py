# -*- coding:utf-8 -*-

""" マルチ決済モジュール
"""

import logging

logger = logging.getLogger(__name__)
from .interfaces import ICardBrandDetecter
from .util import ahead_coms

def multicheckout_dbsession_tween(handler, registry):
    def tween(request):
        try:
            return handler(request)
        finally:
            from .models import _session
            logger.debug('remove multicheckout dbsession')
            _session.remove()
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
    engine = engine_from_config(config.registry.settings, poolclass=NullPool)
    _session.remove()
    _session.configure(bind=engine)

    config.add_tween(".multicheckout_dbsession_tween")

    reg = config.registry
    reg.registerUtility(config.maybe_dotted(".util.detect_card_brand"), 
                        ICardBrandDetecter)

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
