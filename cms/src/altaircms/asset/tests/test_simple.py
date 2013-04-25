import unittest
import altaircms.event.models
import altaircms.models
import altaircms.page.models

class AssetModelUtilitiesTests(unittest.TestCase):
    def _makeOne(self, *args, **kwargs):
        from altaircms.asset.models import ImageAsset
        return ImageAsset(*args, **kwargs)

    def test_filename_with_version(self):
        target = self._makeOne(version_counter=0, filepath="foo.txt")
        self.assertEquals(target.filename_with_version(), "foo.0.txt")

    def test_filename_with_version2(self):
        target = self._makeOne(version_counter=0, filepath="foo.txt")
        self.assertEquals(target.filename_with_version("/dir/bar.txt", 3), "/dir/bar.3.txt")

    def test_all_candidates(self):
        target = self._makeOne(version_counter=0, filepath="/dir/foo.txt")
        result = list(target.all_files_candidates())
        self.assertEquals(result, ["/dir/foo.0.txt"])

    def test_all_candidates2(self):
        target = self._makeOne(version_counter=3, filepath="foo.txt", thumbnail_path="thumb.txt")
        result = list(target.all_files_candidates())
        self.assertEquals(result, ['foo.0.txt', 'foo.1.txt', 'foo.2.txt', 'foo.3.txt', 'thumb.0.txt', 'thumb.1.txt', 'thumb.2.txt', 'thumb.3.txt'])

if __name__ == "__main__":
    unittest.main()
