# -*- coding: utf-8 -*-
from unittest import TestCase
from mock import Mock


class AugusPerformanceImpoterTest(TestCase):
    def _makeOne(self):
        from ..importers import AugusPerformanceImpoter
        return AugusPerformanceImpoter()

    def test_import_record_no_augus_venue(self):
        from ..errors import AugusDataImportError
        augus_account = Mock()
        augus_account.id = 1
        record = Mock()
        record.venue_code = 333
        record.venue_version = 444
        target = self._makeOne()
        with self.assertRaises(AugusDataImportError):
            target.import_record(record, augus_account)
