import unittest

def _getEnv():
    from altaircms.modelmanager.virtualasset import VirtualAssetFactory
    return VirtualAssetFactory("/:static:")

def _getRequest():
    class request:
        environ = {"wsgi.url_scheme": "http"}
        @staticmethod
        def route_path(prefix, subpath):
            return "/".join([prefix, subpath])
    return request

class VirtualAssetsTests(unittest.TestCase):
    def _getTarget(self):
        from altaircms.modelmanager.virtualasset import VirtualAssetModel
        return VirtualAssetModel

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_subpath_found__relativepath(self):
        request, env, obj = _getRequest(), _getEnv(), None
        target = self._makeOne(request, env, obj)
        self.assertEquals(target.route_path("foo/bar.jpg"), "/:static:/foo/bar.jpg")

    def test_subpath_found__abspath(self):
        request, env, obj = _getRequest(), _getEnv(), None
        target = self._makeOne(request, env, obj)
        self.assertEquals(target.route_path("/foo/bar.jpg"), "/foo/bar.jpg")

    def test_subpath_found__url(self):
        request, env, obj = _getRequest(), _getEnv(), None
        target = self._makeOne(request, env, obj)
        self.assertEquals(target.route_path("http://foo/bar.jpg"), "http://foo/bar.jpg")
        self.assertEquals(target.route_path("https://foo/bar.jpg"), "https://foo/bar.jpg")

    def test_subpath_notfound_none(self):
        request, env, obj = _getRequest(), _getEnv(), None
        target = self._makeOne(request, env, obj)
        from altaircms.modelmanager.virtualasset import _NOT_FOUND_IMG
        self.assertEquals(target.route_path(None), _NOT_FOUND_IMG)

    ## image`path
    def test_subpath_notfound__obj_is_none(self):
        request, env, obj = _getRequest(), _getEnv(), None
        target = self._makeOne(request, env, obj)
        from altaircms.modelmanager.virtualasset import _NOT_FOUND_IMG
        self.assertEquals(target.image_path, _NOT_FOUND_IMG)

    def test_subpath_notfound__image_path_is_none(self):
        class obj:
            image_url = None
            image_path = None

        request, env = _getRequest(), _getEnv()
        target = self._makeOne(request, env, obj)
        from altaircms.modelmanager.virtualasset import _NOT_FOUND_IMG
        self.assertEquals(target.image_path, _NOT_FOUND_IMG)

    @unittest.skip ("* #5609: must fix")
    def test_subpath_notfound__image_url_found(self):
        class obj:
            image_url = "s3://:bucket:/foo.jpg"
            image_path = None

        request, env = _getRequest(), _getEnv()
        target = self._makeOne(request, env, obj)
        self.assertEquals(target.image_path, "http://:bucket:.s3.amazonaws.com/foo.jpg")

    def test_subpath_notfound__image_url_found2(self):
        class obj:
            image_url = "http://another/a.jpg"
            image_path = None

        request, env = _getRequest(), _getEnv()
        target = self._makeOne(request, env, obj)
        self.assertEquals(target.image_path, "http://another/a.jpg")

    def test_subpath_notfound__image_path_relative_path(self):
        class obj:
            image_url = None
            image_path = "foo/bar.jpg"

        request, env = _getRequest(), _getEnv()
        target = self._makeOne(request, env, obj)
        self.assertEquals(target.image_path, "/:static:/foo/bar.jpg")


if __name__ == "__main__":
    unittest.main()
