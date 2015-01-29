# -*- coding:utf-8 -*-

def configure_session(config):
    from .models import _session
    from sqlahelper import get_engine
    _session.configure(bind=get_engine())

def includeme(config):
    config.include(configure_session)
    config.include('.communicator')
    config.add_tween('.tweens.anshin_checkout_dbsession_tween_factory')
