#-*- coding: utf-8 -*-
from unittest import TestCase, skip
import os
from altair.augus.exporters import AugusExporter
from altair.augus.parsers import AugusParser
from . import EXAMPLE_DIR

class AugusExporterTest(TestCase):
    PROTOCOLFILE_DIR = EXAMPLE_DIR
    EXPORT_PATH = 'test.csv'

    def test_export(self):
        for name in os.listdir(self.PROTOCOLFILE_DIR):
            path = os.path.join(self.PROTOCOLFILE_DIR, name)
            proto = AugusParser.parse(path)
            AugusExporter.export(proto, self.EXPORT_PATH)
            
            before = after = ''
            with open(path, 'rb') as fp:
                before = fp.read()
            with open(self.EXPORT_PATH, 'rb') as fp:
                after = fp.read()
            self.assertEqual(before, after,
                             'Mismatch data: {} (before: {}, after: {})'\
                             .format(proto.__class__.__name__,
                                     before, after))


