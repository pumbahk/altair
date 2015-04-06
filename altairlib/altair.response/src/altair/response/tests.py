# -*- coding:utf-8 -*-
import unittest
import tempfile
import os
import os.path
import zipfile
import shutil

class FileLikeResponseTest(unittest.TestCase):
    def _makeOne(self, *args, **kwargs):
        from altair.response import FileLikeResponse
        return FileLikeResponse(*args, **kwargs)

    def test_with_seekable(self):
        from io import BytesIO
        io = BytesIO()
        io.write('test')
        resp = self._makeOne(io)
        self.assertEqual(int(resp.headers['Content-Length']), 4)

    def test_with_unseekable(self):
        from socket import socketpair
        s1, s2 = socketpair()
        resp = self._makeOne(s2)
        self.assertNotIn('Content-Length', resp.headers)


class ZipCreateTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from altair.response import ZipFileCreateRecursiveWalk
        return ZipFileCreateRecursiveWalk(*args, **kwargs)()

    def _create_files(self, source_dir):
        with open(os.path.join(source_dir, "a.txt"), "w") as wf:
            wf.write("hello")
        with open(os.path.join(source_dir, "b.txt"), "w") as wf:
            wf.write(u"おはよう".encode("utf-8"))

        os.makedirs(os.path.join(source_dir, "sub"))
        with open(os.path.join(source_dir, "sub", "nested.txt"), "w") as wf:
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

        ## 中身の確認
        with zipfile.ZipFile(zip_path) as z:
            ilist = z.infolist()
            self.assertEqual(len(ilist), 3)

            for i in ilist:
                self.assertTrue(i.filename.endswith(("a.txt", "b.txt", "sub/nested.txt")))

	shutil.rmtree(source_dir)
        os.remove(zip_path)


    def test_it_flatten(self):
        source_dir = tempfile.mkdtemp()
        writename = tempfile.mktemp(".zip")

        self._create_files(source_dir)

        zip_path = self._callFUT(writename, source_dir, flatten=True)

        self.assertTrue(os.path.exists(zip_path))
        self.assertTrue(zipfile.is_zipfile(zip_path))

        ## 中身の確認
        with zipfile.ZipFile(zip_path) as z:
            ilist = z.infolist()
            self.assertEqual(len(ilist), 3)

            for i in ilist:
                self.assertTrue(i.filename.endswith(("a.txt", "b.txt", "nested.txt")))

	shutil.rmtree(source_dir)
        os.remove(zip_path)

