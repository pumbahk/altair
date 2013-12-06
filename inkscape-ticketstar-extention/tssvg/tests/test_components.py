# -*- coding:utf-8 -*-
import unittest

def setUpModule():
    import sys
    import os
    sys.path.append(os.path.join(
        os.path.dirname(os.path.dirname(__name__)),
        "../../"
    ))

class ConfiguratorTests(unittest.TestCase):
    def test_it(self):
        from tssvg import Configurator
config = Configrator()
pango = config.maybe_ffi("libpango-1.0")
gobject = config.maybe_ffi("libgobject-2.0")
print(gobject.g_object_unref.argtypes)
config.setup_ffi("ts_common_library", pango=pango, gobject=gobject)
print(gobject.g_object_unref.argtypes)

if __name__ == '__main__':
    unittest.main()
