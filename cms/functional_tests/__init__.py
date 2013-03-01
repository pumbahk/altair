# -*- coding:utf-8 -*-
import sys
import webtest
import os.path
from paste.deploy.loadwsgi import loadapp
import unittest
import time
from .utils import get_here, set_here

"""
setup

cms: 60543
backend: 60654
"""
_app = None
_registry = None
_config_spec = "config:testing.ini"
_backend_app = None
_lock = None


def setUpModule():
     run_mock_backend_server({})
     build_app()

def tearDownModule():
    from altaircms.models import Base
    Base.metadata.drop_all()
    import shutil
    if os.path.exists(os.path.join(get_here(), "tmp/layouts")):
        shutil.rmtree(os.path.join(get_here(),"tmp/layouts"))
    if os.path.exists(os.path.join(get_here(), "tmp/assets")):
        shutil.rmtree(os.path.join(get_here(),"tmp/assets"))


def build_app():
    global _app
    global _registry
    import altaircms
    here = set_here(os.path.join(altaircms.__path__[0], "../../"))
    _app = loadapp(_config_spec, None,  global_conf={}, relative_to=here)
    _registry = _app.values()[0].registry
    _app = webtest.TestApp(_app, relative_to=os.path.join(here, "functional_tests"))
    return _app

def get_app():
    global _lock
    if not _lock:
        run_mock_backend_server({})
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
    global _lock
    _lock = object()
    from pyramid.config import Configurator
    global_config.update(settings)
    config = Configurator(
        settings=settings,
    )
    def access_token(request):
        ## 本当はaccess tokenが発行された時点でloginではないけれど
        backend = get_backend_app()
        backend.login_status = LOGIN_STATUS["LOGIN"]
        from altaircms.auth.models import DEFAULT_ROLE
        return {u'organization_id': 1,
                u'user_id': 1,
                u'screen_name': u'Administrator-this-is-login-name',
                u'roles': [DEFAULT_ROLE],
                u'access_token': u'429432c429',
                u'organization_name': u'demo-organization',
                u'organization_short_name': u'demo'}

    def logout_backend(request):
        from pyramid.httpexceptions import HTTPFound
        backend = get_backend_app()
        backend.login_status = LOGIN_STATUS["LOGOUT"]

        return HTTPFound(request.GET["return_to"])

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
    def log_message(*args, **kwargs):
        pass
    httpd.log_message = log_message
    th = threading.Thread(target=httpd.serve_forever)
    th.daemon = True
    th.start()


def do_login(app):
    resp = app.get("/auth/login")
    resp.click(linkid="login")

    login_resp = app.get("/auth/oauth_callback")
    import transaction
    transaction.commit()

    login_ok = False
    for k, v in login_resp.headers.iteritems():
        if k == "Set-Cookie" and "cmstkt" in v and "!userid_type:int"in v:
            login_ok = True
    if not login_ok:
        raise Exception("Login Failed. cmstkt is not set")

def do_login_iff_logout(app):
    if not "cmstkt" in app.cookies:
        do_login(app)
    return app

def do_logout_iff_login(app):
    if "cmstkt" in app.cookies:
        do_logout(app)
    return app
    
def do_logout(app):
    app.post("/auth/logout")
    app.reset()
    
class AppFunctionalTests(unittest.TestCase):
    @classmethod
    def _getTarget(cls):
        return get_app()

import contextlib
@contextlib.contextmanager
def login(app):
    do_login_iff_logout(app)
    yield

@contextlib.contextmanager
def logout(app):
    do_logout_iff_login(app)
    yield

def delete_models(models):
    from altaircms.models import DBSession
    for cls in models:
        for e in cls.query:
            DBSession.delete(e)
    import transaction
    transaction.commit()

        
def find_form(forms,  action_part=""):
    for form in forms.itervalues():
        if action_part in form.action:
            return form
   

if __name__ == "__main__":
    unittest.main()
