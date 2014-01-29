#-*- coding: utf-8 -*-
import shutil
import tempfile
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


class MakeDirectoryTest(TestCase):
    def test_it(self):
        from ..utils import mkdir_p
        path = tempfile.mkdtemp()

        if 1:
            mkdir_p(path)
            shutil.rmtree(path)
            mkdir_p(path)

            shutil.rmtree(path, ignore_errors=True)

class GetArgumentParserTest(TestCase):
    def test_it(self):
        from ..utils import get_argument_parser
        parser = get_argument_parser()
        opts = parser.parse_args(['test'])
        self.assertEqual(opts.conf, 'test')
