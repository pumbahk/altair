#-*- coding: utf-8 -*-
from unittest import TestCase
from mock import Mock
from ..utils import RequestAccessor

class TestRequestAccessor(RequestAccessor):
    in_params = {'a': int,
                 'b': str,
                 }
    in_matchdict = {'c': int,
                    'd': str,
                    }

class RequestAccessorTest(TestCase):
    def test_it(self):
        params = Mock()
        params.getall = Mock(return_value=[1,2,3])
        matchdict = {'c': 0,
                     'd': 1,
                     }
        request = Mock()
        request.params = params
        request.matchdict = matchdict
        accessor = TestRequestAccessor(request)
        self.assertEqual(accessor.a, [1,2,3])
        self.assertEqual(accessor.b, map(str, [1,2,3]))
        self.assertEqual(accessor.c, 0)
        self.assertEqual(accessor.d, str(1))
