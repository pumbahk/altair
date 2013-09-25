# -*- coding:utf-8 -*-
import unittest
from . import helpers
from pyramid import testing
from datetime import datetime

class form_logTests(unittest.TestCase):

    def _callFUT(self, *args, **kwargs):
        from .helpers import form_log
        return form_log(*args, **kwargs)


    def test_it(self):
        import logging
        from StringIO import StringIO
        from webob.multidict import MultiDict
        request = testing.DummyRequest(
            params=MultiDict([
                ('aaa', u'日本語ユニコード'),
                ('aaa', '日本語UTF-8'),
                ('a', '10'),
                ('b', '200'),
                ('aa', '1000'),
                ('b', '100'),
            ])
        )
        log_stream = StringIO()
        logger = logging.getLogger('altair.app.ticketing.cart.helpers')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(log_stream)
        formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        self._callFUT(request, "testing")

        self.assertEqual(log_stream.getvalue(), 
            r"""altair.app.ticketing.cart.helpers - INFO - testing: 
[('aaa', u'\u65e5\u672c\u8a9e\u30e6\u30cb\u30b3\u30fc\u30c9'),
 ('aaa', '\xe6\x97\xa5\xe6\x9c\xac\xe8\xaa\x9eUTF-8'),
 ('a', '10'),
 ('b', '200'),
 ('aa', '1000'),
 ('b', '100')]

""")

class helper_Tests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_craete_date_label(self):
        s = datetime(2013, 9, 2)
        e = datetime(2014, 9, 2)
        ret = helpers.create_date_label(s, e)
        self.assertEqual(ret, u"2013年9月2日 - 2014年9月2日")
