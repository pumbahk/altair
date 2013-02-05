# -*- coding:utf-8 -*-
import unittest
from pyramid import testing

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
        logger = logging.getLogger('ticketing.cart.helpers')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(log_stream)
        formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        self._callFUT(request, "testing")

        self.assertEqual(log_stream.getvalue(), 
            r"""ticketing.cart.helpers - INFO - testing: 
[('aaa', u'\u65e5\u672c\u8a9e\u30e6\u30cb\u30b3\u30fc\u30c9'),
 ('aaa', '\xe6\x97\xa5\xe6\x9c\xac\xe8\xaa\x9eUTF-8'),
 ('a', '10'),
 ('b', '200'),
 ('aa', '1000'),
 ('b', '100')]

""")
