from unittest import TestCase
import os
from tempfile import NamedTemporaryFile, mkdtemp

class FileSchemeAssetDescriptorTest(TestCase):
    def _makeTarget(self, path):
        from .file import FileSchemeAssetDescriptor
        return FileSchemeAssetDescriptor(path)

    def test_absspec(self):
        self.assertEquals(self._makeTarget('test').absspec(), "file:test")
        self.assertEquals(self._makeTarget('/test').absspec(), "file:///test")

    def test_stream(self):
        with NamedTemporaryFile() as tmp:
            target = self._makeTarget(tmp.name)
            tmp.write("ABC")
            tmp.flush()
            self.assertEquals(target.stream().read(), "ABC")

    def test_isdir(self):
        with NamedTemporaryFile() as tmp:
            target = self._makeTarget(tmp.name)
            self.assertTrue(not target.isdir())

        tmpdir = mkdtemp()
        try:
            target = self._makeTarget(tmpdir)
            self.assertTrue(target.isdir())
        finally:
            os.rmdir(tmpdir)

    def test_listdir(self):
        tmpdir = mkdtemp()
        files = []
        try:
            for _ in range(0, 10):
                files.append(NamedTemporaryFile(dir=tmpdir))
            target = self._makeTarget(tmpdir)
            self.assertTrue(target.isdir())
            self.assertEqual(set(target.listdir()), set(os.path.basename(file.name) for file in files))
        finally:
            del files
            os.rmdir(tmpdir)

