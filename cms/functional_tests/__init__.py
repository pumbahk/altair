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
here = None

def setUpModule():
    run_mock_backend_server({})
    build_app()

def tearDownModule():
    import sqlahelper
    sqlahelper.get_base().metadata.drop_all()
    import shutil
    shutil.rmtree(os.path.join(here,"tmp/assets"))

def build_app():
    global _app
    global _registry
    global here
    import altaircms
    here = os.path.join(altaircms.__path__[0], "../../")
    _app = loadapp(_config_spec, None,  global_conf={}, relative_to=here)
    _registry = _app.values()[0].registry
    _app = webtest.TestApp(_app, relative_to=os.path.join(here, "functional_tests"))
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


def login(app):
    resp = app.get("/auth/login")
    resp.click(linkid="login")

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
    app.reset()
    
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

            
def find_form(forms,  action_part=""):
    for form in forms.itervalues():
        if action_part in form.action:
            return form
    
class AssetFunctionalTests(AppFunctionalTests):
    def test_login_page_if_not_login(self):
        app = self._getTarget()
        with as_logout(app):
            app.get("/asset/").mustcontain(u"ログインしていません")

    def tearDown(self):
        from altaircms.asset.models import ImageAsset, DBSession
        for a in ImageAsset.query:
            DBSession.delete(a)
        import transaction
        transaction.commit()

    def _count_of_image_asset(self):
        from altaircms.asset.models import ImageAsset
        return ImageAsset.query.count()

    def _get_image_asset_by_title(self, title):
        from altaircms.asset.models import ImageAsset
        return ImageAsset.query.filter_by(title=title).first()

    def _get_static_asset_path(self, path):
        return "/staticasset/"+path

    def test_create_image_asset(self):
        app = self._getTarget()
        self.assertEqual(self._count_of_image_asset(), 0)

        with as_login(app):
            asset_title = u"this-is-created-image-asset"

            form = find_form(app.get("/asset/image").forms, action_part="create")
            form.set("filepath",  ("pyramid.png", ))
            form.set("thumbnail_path", ("pyramid-small.png", ))
            form.set("title", asset_title)
            form.set("tags", "tag0, tag1, tag2")
            form.set("private_tags", "ptag")

            form.submit()

            ## assetが存在
            self.assertEqual(self._count_of_image_asset(), 1)
            created_asset = self._get_image_asset_by_title(asset_title)

            ## 画像が存在
            mainimage = app.get(self._get_static_asset_path(created_asset.filepath))
            self.assertEqual(mainimage.status_int, 200)
            thumbnail_image = app.get(self._get_static_asset_path(created_asset.thumbnail_path))
            self.assertEqual(thumbnail_image.status_int, 200)

    def test_delete_image_asset(self):
        app = self._getTarget()
        self.assertEqual(self._count_of_image_asset(), 0)

        with as_login(app):
            asset_title = u"this-is-created-image-asset"

            form = find_form(app.get("/asset/image").forms, action_part="create")
            form.set("filepath",  ("pyramid.png", ))
            form.set("thumbnail_path", ("pyramid-small.png", ))
            form.set("title", asset_title)
            form.set("tags", "tag0, tag1, tag2")
            form.set("private_tags", "ptag")

            form.submit()

            ## assetが存在
            self.assertEqual(self._count_of_image_asset(), 1)
            created_asset = self._get_image_asset_by_title(asset_title)

            ### delete
            form = find_form(app.get("/asset/image/%s/delete" % created_asset.id).forms, action_part="delete").submit()
            
            ## assetがなくなる
            self.assertEqual(self._count_of_image_asset(), 0)

            ## 画像が消える
            with self.assertRaises(webtest.AppError):
                app.get(self._get_static_asset_path(created_asset.filepath))
                app.get(self._get_static_asset_path(created_asset.thumbnail_path))


    def test_update_image_asset(self):
        app = self._getTarget()
        self.assertEqual(self._count_of_image_asset(), 0)

        with as_login(app):
            ## create
            asset_title = u"this-is-created-image-asset"

            form = find_form(app.get("/asset/image").forms, action_part="create")
            form.set("filepath",  ("pyramid.png", ))
            form.set("thumbnail_path", ("pyramid-small.png", ))
            form.set("title", asset_title)
            form.set("tags", "tag0, tag1, tag2")
            form.set("private_tags", "ptag")

            form.submit()

            created_asset = self._get_image_asset_by_title(asset_title)
            created_asset_size = created_asset.size
            created_asset_filepath = created_asset.filepath


            ### update title
            asset_title = u"update-asset"

            form = find_form(app.get("/asset/image/%s/input" % created_asset.id).forms, action_part="update")
            form.set("filepath",  "")
            form.set("thumbnail_path", "")
            form.set("title", asset_title)
            form.set("tags", "tag-is-updated")
            form.set("private_tags", "ptag, ptag2")

            form.submit()

            ## タイトルは変わる
            self.assertEqual(self._count_of_image_asset(), 1)
            updated_asset = self._get_image_asset_by_title(asset_title)
            self.assertEqual(updated_asset.title, asset_title)

            ## 画像は変わらない
            self.assertEqual(updated_asset.size,  created_asset.size)            
            self.assertEqual(updated_asset.filepath, created_asset_filepath)


            ### update image
            created_asset = self._get_image_asset_by_title(asset_title)
            asset_title = u"update-asset"

            form = find_form(app.get("/asset/image/%s/input" % created_asset.id).forms, action_part="update")
            form.set("filepath",  ("not_found.png", ))
            form.set("thumbnail_path", "")
            form.set("title", asset_title)
            form.set("tags", "tag-is-updated")
            form.set("private_tags", "ptag, ptag2")

            form.submit()

            self.assertEqual(self._count_of_image_asset(), 1)
            updated_asset2 = self._get_image_asset_by_title(asset_title)
            
            ## 画像を変更しても保存先は変わらない
            self.assertEqual(updated_asset2.filepath, created_asset.filepath)
            self.assertEqual(updated_asset2.filepath, created_asset_filepath)

            ## ただし保存されているファイルは変わる
            self.assertNotEqual(updated_asset2.size, created_asset_size)
            
        
if __name__ == "__main__":
    unittest.main()
