import unittest
from pyramid import testing
import json
import mock

def _make_router(config):
    from pyramid.router import Router
    router = Router(config.registry)
    return router

def _make_request(registry=None, path=None, **kwargs):
    request = testing.DummyRequest(path=path, **kwargs)            
    if registry:
        request.__dict__["registry"] = registry
    if path:
        request.environ["PATH_INFO"] = path
    if request.GET:
        request.params = request.GET
    if request.POST:
        request.params = request.POST
    return request
    
class APIViewDispatchTests(unittest.TestCase):
    def tearDown(self):
        testing.tearDown()

    def setUp(self):
        self.config = testing.setUp()        

    def test_router_dummy_view_is_exactly_select(self):
        config = self.config
        config.add_route("home", "/")
        config.add_view(lambda r: "this-is-view-result", renderer="string", route_name="home")

        router = _make_router(config)
        request = _make_request(path="/", registry=config.registry)
        response = router.handle_request(request)
        self.assertEqual(response.body, "this-is-view-result")

    @mock.patch("altair.app.ticketing.tickets.preview.views.PreviewApiView.preview_ticket_post64")
    def test_it(self, m):
        m.return_value = {"result": "preview.base64 is called"}

        config = self.config
        config.add_renderer('.html' , 'pyramid.mako_templating.renderer_factory')
        config.include('altair.app.ticketing.tickets.preview.include_views')
        router = _make_router(config)


        request = _make_request(path="/api/preview/preview.base64",
                                post={"svg": "this-is-svg-data"}, 
                                registry=config.registry)
        result = router.handle_request(request)
        self.assertEqual(result.body, json.dumps({"result": "preview.base64 is called"}))

    @mock.patch("altair.app.ticketing.tickets.preview.views.PreviewApiView.preview_ticket_post64_sej")
    def test_call_with_sej(self, m):
        m.return_value = {"result": "sej version is called"}

        config = self.config
        config.add_renderer('.html' , 'pyramid.mako_templating.renderer_factory')
        config.include('altair.app.ticketing.tickets.preview.include_views')
        router = _make_router(config)


        request = _make_request(path="/api/preview/preview.base64",
                                post={"type": "sej", "svg": "this-is-svg-data"}, 
                                registry=config.registry)
        result = router.handle_request(request)
        self.assertEqual(result.body, json.dumps({"result": "sej version is called"}))

if __name__ == "__main__":
    unittest.main()

