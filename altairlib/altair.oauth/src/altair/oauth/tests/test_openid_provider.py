import logging
import unittest
import mock
import inspect

from ..exceptions import OpenIDNoSuchIDTokenError


class DummyHandler(logging.Handler):
    def __init__(self, *args, **kwargs):
        logging.Handler.__init__(self, *args, **kwargs)
        self.records = []

    def emit(self, record):
        self.records.append(record)


class LoggingContext(object):
    def __init__(self, logger):
        self.logger = logger

    def __enter__(self):
        self.dummy_handler = DummyHandler(logging.DEBUG)
        self.prev_level = self.logger.getEffectiveLevel()
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(self.dummy_handler)
        return self.dummy_handler

    def __exit__(self, type, value, traceback):
        self.logger.removeHandler(self.dummy_handler)
        self.logger.setLevel(self.prev_level)


class OpenIDProviderTest(unittest.TestCase):
    def _getTarget(self):
        from ..openid_provider import OpenIDProvider
        return OpenIDProvider

    def  _makeOne(self, **kwargs):
        return self._getTarget()(**kwargs)

    def test_get_authn_descriptor_by_id_token_nonexistent(self):
        oauth_provider = mock.Mock()
        id_token_store = mock.Mock()
        target = self._makeOne(
            oauth_provider=oauth_provider,
            id_token_store=id_token_store,
            issuer=u'xxx',
            token_expiration_time=300,
            secret=u'secret',
            jws_algorithm=u'HS256',
            )
        with LoggingContext(inspect.getmodule(target).logger) as handler:
            try:
                target.get_authn_descriptor_by_id_token(u'id_token')
                self.fail()
            except OpenIDNoSuchIDTokenError as e:
                pass
        self.assertEqual(handler.records[0].msg, 'id_token (id_token) does not exist')

    def test_get_authn_descriptor_by_id_token_expired(self):
        from datetime import datetime
        oauth_provider = mock.Mock()
        id_token_store = mock.MagicMock()
        id_token_store.__getitem__.return_value = dict(
            expire_at=datetime(2016, 1, 1, 0, 0, 0) 
            )
        target = self._makeOne(
            oauth_provider=oauth_provider,
            id_token_store=id_token_store,
            issuer=u'xxx',
            token_expiration_time=300,
            secret=u'secret',
            jws_algorithm=u'HS256',
            )
        with LoggingContext(inspect.getmodule(target).logger) as handler:
            try:
                target.get_authn_descriptor_by_id_token(u'id_token')
                self.fail()
            except OpenIDNoSuchIDTokenError as e:
                pass
        self.assertEqual(handler.records[0].msg, 'id_token (id_token) expired at 2016-01-01 00:00:00')
