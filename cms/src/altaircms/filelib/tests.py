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

        self.assertEqual(target.creator.pool, [result])

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

    def test_create_file_on_does_not_exist_directory(self):
        from StringIO import StringIO
        import os
        import shutil
        content = StringIO("this-is-file-content")

        target = self._makeOne(prefix=".")
        f = self._createFile(name="foo/bar/baz/this-is-name", handler=content)

        target.add(f)
        target.commit()

        realpath = os.path.join(target.make_path(), f.name)
        self.assertTrue(os.path.exists(realpath))
        shutil.rmtree("./foo")

    def test_overwrite(self):
        from StringIO import StringIO
        import os
        with open("./foo.txt", "w") as rf:
            rf.write("first")

        target = self._makeOne(prefix=".")
        f = self._createFile(name="foo.txt", handler=StringIO("this-is-second"))

        target.add(f)
        self.assertEqual(open("./foo.txt").read(), "first")

        target.commit()
        self.assertEqual(open("./foo.txt").read(), "this-is-second")
        target.delete("foo.txt")
        target.commit()
        self.assertTrue(not os.path.exists("./foo.txt"))

    def test_delete(self):
        import os.path
        from tempfile import mktemp

        outfilename = mktemp()
        with open(outfilename, "w") as wf:
            wf.write("heh")

        target = self._makeOne(prefix="")
        f = self._createFile(name=outfilename, handler=None)

        self.assertTrue(os.path.exists(outfilename))
        target.delete(f)
        self.assertTrue(os.path.exists(outfilename))
        target.commit()
        self.assertFalse(os.path.exists(outfilename))

    def test_delete_with_string(self):
        import os.path
        from tempfile import mktemp

        outfilename = mktemp()
        with open(outfilename, "w") as wf:
            wf.write("heh")

        target = self._makeOne(prefix="")
        self.assertTrue(os.path.exists(outfilename))
        target.delete(outfilename)
        self.assertTrue(os.path.exists(outfilename))
        target.commit()
        self.assertFalse(os.path.exists(outfilename))

    def test_delete_with_not_existfilename(self):
        import os.path
        from tempfile import mktemp

        outfilename = mktemp()
        target = self._makeOne(prefix="")
        self.assertFalse(os.path.exists(outfilename))
        target.delete(outfilename)
        target.commit()
        self.assertFalse(os.path.exists(outfilename))

if __name__ == "__main__":
    unittest.main()
