import unittest

class FileSaveTests(unittest.TestCase):
    def _getTargetClass(self):
        from altaircms.filelib.core import FileSession
        return FileSession

    def _makeOne(self, *args, **kwargs):
        return self._getTargetClass()(*args, **kwargs)

    def _createFile(self, **kwargs):
        from altaircms.filelib.core import File
        return File(**kwargs)

    def test_add_get_signatured(self): ##this is integration
        from StringIO import StringIO
        import os
        content = StringIO("this-is-file-content")

        target = self._makeOne(prefix=".")
        f = self._createFile(name="this-is-name", handler=content)
        result = target.add(f)

        self.assertEqual(target.pool, [result])

        self.assertEqual(result.name, f.name)
        self.assertEqual(result.handler, f.handler)

        self.assertTrue(os.path.exists(result.signature))
        os.remove(result.signature)

    def test_add_and_commit_when_move_to_realpath(self):
        from StringIO import StringIO
        import os
        content = StringIO("this-is-file-content")

        target = self._makeOne(prefix=".")
        f = self._createFile(name="this-is-name", handler=content)

        target.add(f)
        target.commit()

        realpath = os.path.join(target.make_path(), f.name)
        self.assertTrue(os.path.exists(realpath))
        os.remove(realpath)

if __name__ == "__main__":
    unittest.main()
