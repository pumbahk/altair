# -*- coding:utf-8 -*-
import unittest
import tempfile
import os
import os.path
import zipfile

class ZipCreateTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from altair.response import ZipFileCreateRecursiveWalk
        return ZipFileCreateRecursiveWalk(*args, **kwargs)()

    def _create_files(self, source_dir):
        with open(os.path.join(source_dir, "a.txt"), "w") as wf:
            wf.write("hello")
        with open(os.path.join(source_dir, "b.txt"), "w") as wf:
            wf.write(u"おはよう".encode("utf-8"))

        os.makedirs(os.pathos.path.join(source_dir, "sub"))
        with open(os.path.join(source_dir, "sub", "nested.txt")) as wf:
            wf.write("nested\n")
            wf.write("nested\n")
            wf.write("nested\n")

    def test_it(self):
        source_dir = tempfile.mkdtemp()
        writename = tempfile.mktemp(".zip")

        self._create_files(source_dir)

        zip_path = self._callFUT(writename, source_dir)

        self.assertTrue(os.path.exists(zip_path))
        self.assertTrue(zipfile.is_zipfile(zip_path))
        print(zip_path) #xxx:

