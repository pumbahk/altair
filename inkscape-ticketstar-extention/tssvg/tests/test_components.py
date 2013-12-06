# -*- coding:utf-8 -*-
import unittest
import sys
import os

def setUpModule():
    sys.path.append(os.path.join(
        os.path.abspath(os.path.dirname(os.path.dirname(__file__))),
        "../"
    ))

class ConfiguratorTests(unittest.TestCase):
    def _makeOne(self, *args, **kwargs):
        from tssvg import Configurator
        return Configurator(*args, **kwargs)

    def test_maybe_ffi__string(self):
        from ctypes import CDLL
        from ctypes.util import find_library
        loader = CDLL
        finder = find_library
        target = self._makeOne(loader, finder)

        result = target.maybe_ffi("libc")
        self.assertTrue(result.printf)

    def test_maybe_ffi__object(self):
        from ctypes import CDLL
        from ctypes.util import find_library
        loader = CDLL
        finder = find_library
        target = self._makeOne(loader, finder)

        libc = CDLL(find_library("libc"))
        result = target.maybe_ffi(libc)
        self.assertEqual(result, libc)


    def test_include_resolver(self):
        loader = None
        finder = None
        target = self._makeOne(loader, finder)

        called = []
        def include_resolver(config, *args, **kwargs):
            called.append((args, kwargs))
            for k, v in kwargs.items():
                setattr(config, k, v)

        target.include_resolver(include_resolver, ffix="ffix", ffiy="ffiy")
        self.assertEqual(called[0][0], ())
        self.assertEqual(called[0][1], {"ffix": "ffix", "ffiy":"ffiy"})

if __name__ == '__main__':
    unittest.main()
