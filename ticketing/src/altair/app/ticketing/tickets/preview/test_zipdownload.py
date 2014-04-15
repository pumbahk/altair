# -*- coding:utf-8 -*-
import tempfile
import logging
import zipfile
import os
logger = logging.getLogger(__name__)

import unittest

class ZipDownloadTests(unittest.TestCase):
    def _getTarget(self):
        from altair.app.ticketing.tickets.preview.views import DownloadListOfPreviewImage
        return DownloadListOfPreviewImage

    def test_zip_create(self):
        context = None
        request = None
        target = self._getTarget()(context, request)
        tmpdir = tempfile.mkdtemp()
        with open(os.path.join(tmpdir, "sample.txt"), "w") as wf:
            wf.write("sample")
        zippath = tempfile.mktemp("sample.zip")
        walk = target.create_zip_file_creator(zippath, tmpdir)
        walk()

        self.assertTrue(os.path.exists(zippath))
        self.assertTrue(zipfile.is_zipfile(zippath))

    def test_zip_create__with_monkey_patched(self):
        import altair.app.ticketing.sej.zip_file
        import zipfile
        self.assertNotEqual(zipfile.structCentralDir, "<4s4B4HL2L5H2L")

        context = None
        request = None
        target = self._getTarget()(context, request)
        tmpdir = tempfile.mkdtemp()
        with open(os.path.join(tmpdir, "sample.txt"), "w") as wf:
            wf.write("sample")
        zippath = tempfile.mktemp("sample.zip")
        walk = target.create_zip_file_creator(zippath, tmpdir)
        walk()

        self.assertTrue(os.path.exists(zippath))
        self.assertTrue(zipfile.is_zipfile(zippath))
