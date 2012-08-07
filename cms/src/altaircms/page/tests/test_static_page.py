# -*- encoding:utf-8 -*-
from datetime import datetime
import unittest
import os
from pyramid import testing
# from altaircms.testing import setup_db
# from altaircms.testing import teardown_db
from altaircms.testing import DummyRequest
from altaircms.testing import DummyFileStorage

import mock

# def setUpModule():
#     setup_db(["altaircms.event.models", 
#               "altaircms.page.models"])

# def tearDownModule():
#     teardown_db()

class StaticPageUtilityTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from altaircms.page.api import get_static_page_utility
        return get_static_page_utility(*args, **kwargs)

    def tearDown(self):
        testing.tearDown()

    def test_enable_utility(self):
        config = testing.setUp()
        config.maybe_dotted("altaircms.page.api.set_static_page_utility")(
            config,
            "altaircms.page.tests:.",
            os.path.abspath("."))

        request = testing.DummyRequest()
        result = self._callFUT(request)
        self.assertTrue(result)
        
    def test_usable_asset_spec_or_abspath(self):
        config = testing.setUp()
        config.maybe_dotted("altaircms.page.api.set_static_page_utility")(
            config,
            "altaircms.page.tests:.",
            os.path.abspath(os.path.dirname(__file__)))

        request = testing.DummyRequest()
        result = self._callFUT(request)

        self.assertEquals(os.path.normpath(result.basedir),
                          os.path.normpath(os.path.abspath(os.path.dirname(__file__))))

        self.assertEquals(os.path.normpath(result.tmpdir),
                          os.path.normpath(os.path.abspath(os.path.dirname(__file__))))

    def test_not_accessable_path(self):
        from pyramid.exceptions import ConfigurationError

        config = testing.setUp()
        with self.assertRaises(ConfigurationError):
            config.maybe_dotted("altaircms.page.api.set_static_page_utility")(
                config,
                "/", "/tmp")

        with self.assertRaises(ConfigurationError):
            config.maybe_dotted("altaircms.page.api.set_static_page_utility")(
                config,
                "/tmp", "/")


class StaticPageCreateViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.maybe_dotted("altaircms.page.api.set_static_page_utility")(
            self.config, "altaircms.page.tests:.", "altaircms.page.tests:."
        )
        
    def tearDown(self):
        testing.tearDown()

    def _getTarget(self):
        from altaircms.page.views import StaticPageCreateView
        return StaticPageCreateView

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args,**kwargs)

    def test_create_object(self):
        self.config.add_route("static_page", "/page/static/{static_page_id}/{action}", 
                              factory="altaircms.page.resources.StaticPageResource")

        tester = self
        class DummyContext(object):
            def __init__(self, request):
                self.request = request
                self.called = []
                
            def create_static_page(self, data):
                tester.assertEquals(data["name"], postdata["name"])

                self.called.append("create_static_page")
                return testing.DummyResource(name=data["name"], id=1)

        postdata = dict(name="this-is-static-page-name", 
                        zipfile=DummyFileStorage("filename.zip", "content-of-zip"))
        request = DummyRequest(POST=postdata)
        context = DummyContext(request)
        target = self._makeOne(context, request)

        with mock.patch("altaircms.page.writefile.replace_directory_from_zipfile") as m:
            with mock.patch("altaircms.page.forms.StaticPageCreateForm") as fm: 
                fm.validate.return_value = True
                fm().data = postdata

                target.create()
                self.assertEquals(context.called, ["create_static_page"])

            self.assertEquals(m.call_count, 1)
            args, _ = m.call_args
            self.assertEquals(os.path.normpath(args[0]), 
                              os.path.join(os.path.abspath(os.path.dirname(__file__)), "this-is-static-page-name"))
            self.assertEquals(args[1], postdata["zipfile"].file)


class StaticPageViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.maybe_dotted("altaircms.page.api.set_static_page_utility")(
            self.config, "altaircms.page.tests:.", "altaircms.page.tests:."
        )
        
    def tearDown(self):
        testing.tearDown()

    def _getTarget(self):
        from altaircms.page.views import StaticPageView
        return StaticPageView

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args,**kwargs)

    def test_delete_object(self):
        from altaircms.page.models import StaticPage
        self.config.add_route('pageset_list', '/page/{kind}/list')

        request = DummyRequest(matchdict={"static_page_id": 1})
        obj = StaticPage(name="foo", id=1)

        with mock.patch("altaircms.page.views.get_or_404") as mFinder:
            mFinder.return_value = obj
            with mock.patch("altaircms.page.writefile.create_directory_snapshot") as mWriteFile:
                with mock.patch("altaircms.page.resources.StaticPageResource") as mResource:
                    target = self._makeOne(mResource(), request)
                    target.delete()
                    
                    self.assertEquals(mResource().delete_static_page.call_count, 1)
                    args, kwargs = mResource().delete_static_page.call_args
                    self.assertEquals(args, (obj,))

                self.assertEquals(mWriteFile.call_count, 1)
                args, kwargs = mWriteFile.call_args
                self.assertEquals(os.path.normpath(args[0]), os.path.join(os.path.abspath(os.path.dirname(__file__)), "foo"))
            
    def test_update_object(self):
        from altaircms.page.models import StaticPage
        self.config.add_route("static_page", "/page/static/{static_page_id}/{action}")

        request = DummyRequest(matchdict={"static_page_id": 1}, 
                               POST=dict(zipfile=DummyFileStorage("foo.zip", "this-is-content-of-zip")))
        obj = StaticPage(name="foo", id=1)

        with mock.patch("altaircms.page.views.get_or_404") as mFinder:
            mFinder.return_value = obj
            with mock.patch("altaircms.page.views.writefile") as mWriteFile:
                mWriteFile.create_directory_snapshot = mock.Mock()
                mWriteFile.is_zipfile = mock.Mock(return_value=True)

                with mock.patch("altaircms.page.resources.StaticPageResource") as mResource:
                    target = self._makeOne(mResource(), request)
                    target.upload()
                    
                    self.assertEquals(mResource().touch_static_page.call_count, 1)
                    args, kwargs = mResource().touch_static_page.call_args
                    self.assertEquals(args, (obj,))

                saved_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), ".", "foo")
                args, kwargs = mWriteFile.create_directory_snapshot.call_args
                self.assertEquals(args, (saved_path,))
                
                args, kwargs = mWriteFile.replace_directory_from_zipfile.call_args
                self.assertEquals(args, (saved_path, request.POST["zipfile"].file))

    def test_update_object_failcase(self):
        from altaircms.page.models import StaticPage
        from pyramid.httpexceptions import HTTPFound

        self.config.add_route("static_page", "/page/static/{static_page_id}/{action}")

        request = DummyRequest(matchdict={"static_page_id": 1}, 
                               POST=dict(zipfile=DummyFileStorage("foo.zip", "this-is-content-of-zip")))
        obj = StaticPage(name="foo", id=1)

        with mock.patch("altaircms.page.views.get_or_404") as mFinder:
            mFinder.return_value = obj
            with mock.patch("altaircms.page.views.writefile") as mWriteFile:
                mWriteFile.is_zipfile = mock.Mock(return_value=False)
                with mock.patch("altaircms.page.resources.StaticPageResource") as mResource:
                    target = self._makeOne(mResource(), request)

                    self.assertRaises(HTTPFound, lambda : target.upload())


class StaticPageResourceTest(unittest.TestCase):
    def _getTarget(self):
        from altaircms.page.resources import StaticPageResource
        return StaticPageResource

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)
        
    def test_create(self):
        with mock.patch("altaircms.page.resources.DBSession") as mSession:
            with mock.patch("altaircms.page.resources.notify_model_create") as mSubscriber:
                request = DummyRequest()
                target = self._makeOne(request)
                data = {"name": "this-is-static-page-name"}
                target.create_static_page(data)

                self.assertEquals(mSubscriber.call_count, 1)
                self.assertEquals(mSubscriber.call_args[0][0], request)
                from altaircms.page.models import StaticPage
                self.assertEquals(type(mSubscriber.call_args[0][1]), StaticPage)
                self.assertEquals(mSubscriber.call_args[0][1].name, "this-is-static-page-name")
                self.assertEquals(mSubscriber.call_args[0][2], dict(name="this-is-static-page-name"))

                self.assertEquals(mSession.add.call_count, 1)
                self.assertEquals(mSession.add.call_args[0][0].name, "this-is-static-page-name")

                self.assertEquals(mSession.flush.call_count, 1)

    def test_delete(self):
        with mock.patch("altaircms.page.resources.DBSession") as mSession:
            request = DummyRequest()
            target = self._makeOne(request)
            static_page = object()
            target.delete_static_page(static_page)

            self.assertEquals(mSession.delete.call_count, 1)
            self.assertEquals(mSession.delete.call_args[0], (static_page, ))

    def test_touch(self):
        from altaircms.page.models import StaticPage
        with mock.patch("altaircms.page.resources.DBSession") as mSession:
            request = DummyRequest()
            target = self._makeOne(request)

            static_page = StaticPage()
            self.assertEquals(static_page.updated_at, None)

            result = target.touch_static_page(static_page, _now=lambda : datetime(1900, 1, 1))

            self.assertEquals(result.updated_at, datetime(1900, 1, 1))
            self.assertEquals(mSession.add.call_count, 1)
            self.assertEquals(mSession.add.call_args[0], (static_page, ))



if __name__ == "__main__":
    unittest.main()
