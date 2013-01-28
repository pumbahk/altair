# -*- coding:utf-8 -*-
import sys
import webtest
import os.path
from paste.deploy.loadwsgi import loadapp
import unittest
import time

"""
setup

cms: 60543
backend: 60654
"""
_app = None
_registry = None
_config_spec = "config:testing.ini"
_backend_app = None

def setUpModule():
    run_mock_backend_server({})
    build_app()

def tearDownModule():
    import sqlahelper
    sqlahelper.get_base().metadata.drop_all()

def build_app():
    global _app
    global _registry
    import altaircms
    here = os.path.join(altaircms.__path__[0], "../../")
    _app = loadapp(_config_spec, None,  global_conf={}, relative_to=here)
    _registry = _app.values()[0].registry
    _app = webtest.TestApp(_app)
    return _app

def get_app():
    while not _backend_app:
        sys.stderr.write("wait for runnnig backend server\n")
        time.sleep(0.1)
    if not _app:
        return build_app()
    return _app

def get_backend_app():
    return _backend_app

def get_registry():
    return _registry


## backend mock for login
LOGIN_STATUS = {
    "LOGIN": "login", 
    "LOGOUT": "logout", 
    "NOTSET": "notset"
    }

def mock_backend_main(global_config, **settings):
    from pyramid.config import Configurator
    global_config.update(settings)
    config = Configurator(
        settings=settings,
    )
    def access_token(request):
        ## 本当はaccess tokenが発行された時点でloginではないけれど
        backend = get_backend_app()
        backend.login_status = LOGIN_STATUS["LOGIN"]

        return {u'organization_id': 1,
                u'user_id': 1,
                u'screen_name': u'Administrator-this-is-login-name',
                u'roles': [u'administrator'],
                u'access_token': u'429432c429',
                u'organization_name': u'demo-organization',
                u'organization_short_name': u'demo'}

    def logout_backend(request):
        from pyramid.httpexceptions import HTTPRedirect
        backend = get_backend_app()
        backend.login_status = LOGIN_STATUS["LOGOUT"]

        return HTTPRedirect(request.GET["return_to"])

    config.add_route("auth.access_token", "/api/access_token")
    config.add_view(access_token, route_name="auth.access_token",  renderer="json")
    config.add_route("auth.logout", "/api/forget_loggedin")
    config.add_view(logout_backend, route_name="auth.logout")
    return config.make_wsgi_app()

def run_mock_backend_server(data, port=60654):
    from wsgiref.simple_server import make_server
    import threading
    global _backend_app
    _backend_app = mock_backend_main({})

    _backend_app.login_status = "none"

    httpd = make_server('0.0.0.0', port, _backend_app)
    httpd.log_message = lambda *args, **kwargs: None
    th = threading.Thread(target=httpd.handle_request)
    th.setDaemon(True)
    th.start()



def login(app):
    login_resp = app.get("/auth/oauth_callback")
    
    login_ok = False
    for k, v in login_resp.headers.iteritems():
        if k == "Set-Cookie" and "cmstkt" in v and "!userid_type:int"in v:
            login_ok = True
    if not login_ok:
        raise Exception("Login Failed. cmstkt is not set")

def login_iff_logout(app):
    if not "cmstkt" in app.cookies:
        login(app)
    return app

def logout_iff_login(app):
    if "cmstkt" in app.cookies:
        logout(app)
    return app
    
def logout(app):
    app.post("/auth/logout")
    
class AppFunctionalTests(unittest.TestCase):
    def _getTarget(self):
        return get_app()

import contextlib
@contextlib.contextmanager
def as_login(app):
    login_iff_logout(app)
    yield

@contextlib.contextmanager
def as_logout(app):
    logout_iff_login(app)
    yield


class LoginLogoutFunctionalTests(AppFunctionalTests):
    """
    cms[login] ---- redirect ---> backend[login]
                                     |
    cms[after] <--- redirect ---- backend[login] OK
    """
    def test_login_redirect(self):
        app = self._getTarget()

        with as_logout(app):
            resp = app.get("/auth/login")
            self.assertEqual(resp.status_int, 200)

            login_resp = resp.click(linkid="login")
            self.assertEqual(login_resp.status_int, 302)

            client_id = get_registry().settings["altair.oauth.client_id"]
            login_resp.mustcontain(client_id)

    def test_after_backend_login_redirect(self):
        app = self._getTarget()
        with as_login(app):
            login_iff_logout(app)

            ## login後、loginしたorganization名が右上に表示される
            after_login_resp = app.get("/")
            after_login_resp.mustcontain("Administrator-this-is-login-name")        
            after_login_resp.mustcontain("demo-organization")

    def test_after_logout_redirect(self):
        app = self._getTarget()
        with as_login(app):
            logout(app)
            after_logout_resp = app.get("/")

            ### logout後はlogin情報見えない
            self.assertNotIn("Admoutistrator-this-is-login-name", after_logout_resp.ubody)
            self.assertNotIn("demo-organization",  after_logout_resp)

            
class AssetFunctionalTests(AppFunctionalTests):
    def test_login_page_if_not_login(self):
        app = self._getTarget()
        with as_logout(app):
            app.get("/asset/").mustcontain(u"ログインしていません")

    def test_view_index_page(self):
        app = self._getTarget()
        with as_login(app):
            app.get("/asset/").mustcontain(u"アセット一覧")

        
if __name__ == "__main__":
    unittest.main()
