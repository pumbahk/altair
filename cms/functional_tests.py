# -*- coding:utf-8 -*-

"""
機能テストはここでのみ行うこと
"""

import unittest
import webtest


test_settings = {
    "sqlalchemy.url": "sqlite:///",
    "sqlalchemy.echo": "false",
    "altaircms.debug.strip_security": "false",
    "altaircms.layout_directory": "altaircms:templates/front/layout",
    "altaircms.plugin_static_directory":  "altaircms:plugins/static",
    "authtkt.secret": 'authtkt-secret',
    "session.secret": 'session-secret',
    "pyramid.includes": __name__,
    }


def make_mock_oauth_provider(global_config, **settings):
    from pyramid.config import Configurator
    from pyramid.httpexceptions import HTTPFound

    def access_token_view(request):
        return dict(user_id=settings['user_id'],
                    screen_name=settings['screen_name'],
                    access_token=settings['access_token'])

    def authorize(request):
        return HTTPFound(location='http://localhost:6543/auth/oauth_callback')

    config = Configurator()
    config.add_route('access_token', '/api/access_token')
    config.add_route('authorize', '/login/authorize')
    config.add_view(access_token_view, route_name='access_token', renderer='json')
    config.add_view(authorize, route_name='authorize')
    app = config.make_wsgi_app()
    return app

def run_oauth_provider(user_id, screen_name, access_token, port=7654):

    settings = dict(
        user_id=user_id,
        screen_name=screen_name,
        access_token=access_token,
        )
    app = make_mock_oauth_provider({}, **settings)

    from wsgiref.simple_server import make_server
    httpd = make_server('0.0.0.0', port, app)
    httpd.log_message = lambda *args, **kwargs: None
    import threading
    th = threading.Thread(target=httpd.handle_request)
    th.start()

def paste_fixture(event):
    fixture_values = dict(event)
    request = event['request']
    if 'paste.testing' in request.environ:
        request.environ['paste.testing_variables']['render_event'] = fixture_values
        

def includeme(config):
    config.add_subscriber(paste_fixture,
                          'pyramid.events.BeforeRender')

def _login_header(cookie_name, secret, user_id, ip="0.0.0.0"):
    from pyramid.authentication import AuthTicket
    ticket = AuthTicket(secret, user_id, ip)
    return [('Cookie', '%s=%s' % (cookie_name, ticket.cookie_value()))]


def _getTarget():
    global app
    return webtest.TestApp(app)


def _setup_user(user_id, role='administrator'):
    # ログインユーザーはフィクスチャで作ってしまってよい
    from altaircms.auth.models import Operator, Role
    import sqlahelper
    admin_role = Role.query.filter_by(name=role).one()
    sqlahelper.get_session().add(Operator(user_id=user_id, auth_source='oauth', role=admin_role))

def _delete_user(self, user_id):
    from altaircms.auth.models import Operator
    Operator.query.filter_by(user_id='this-is-user-id').delete()

app = None
store = None

def _setup_app(store):
    from altaircms import main
    settings = test_settings.copy()
    settings['altaircms.asset.storepath'] = store
    app = main({}, **settings)
    return app

def _setup_db():
    import sqlahelper
    sqlahelper.get_base().metadata.drop_all()
    sqlahelper.get_base().metadata.create_all()
    from altaircms.auth.models import Role
    role = Role(name='administrator')
    session = sqlahelper.get_session()
    session.add(role)

def _teardown_db():
    import sqlahelper
    sqlahelper.get_base().metadata.drop_all()
    

def setup_module():
    global app
    global store
    import tempfile
    import transaction
    store = tempfile.mkdtemp()
    app = _setup_app(store)
    _setup_db()
    _setup_user('fixture-user')
    transaction.commit()

def teardown_module():
    _teardown_db()
    import shutil
    shutil.rmtree(store)


class BaseFunctionalTests(unittest.TestCase):


    def _add_api_key(self, name):
        import sqlahelper
        from altaircms.auth.models import APIKey
        key = APIKey(name=name)
        session = sqlahelper.get_session()
        session.add(key)
        session.flush()
        key_id = key.id
        import transaction
        transaction.commit()

        return key_id

    def _delete_api_key(self, name):
        import sqlahelper
        from altaircms.auth.models import APIKey
        APIKey.query.filter(APIKey.name==name).delete()
        import transaction
        transaction.commit()




    def test_dashboard(self):
        app = _getTarget()

        res = app.get('/')

    def test_apikey_list_GET(self):
        app = _getTarget()

        res = app.get('/apikey/')

    def test_apikey_list_POST(self):
        app = _getTarget()

        res = app.post('/apikey/', params={'name': 'this-is-api-key'})

        self.assertEqual(res.location, 'http://localhost/apikey/')

    def test_apikey(self):

        app = _getTarget()
        id = self._add_api_key('this-is-api-key')
        res = app.post('/apikey/%d' % id, params={'_method': 'delete'})
        self._delete_api_key("this-is-api-key")

class AuthFunctionalTests(unittest.TestCase):

    def test_login(self):
        app = _getTarget()
        app.get('/auth/login')

    def test_logout(self):
        app = _getTarget()
        app.get('/auth/logout')

    def test_oauth_entry(self):
        app = _getTarget()
        app.get('/auth/oauth')
    
    def test_oauth_callback(self):
        app = _getTarget()
        run_oauth_provider(user_id='this-is-user_id', 
                           screen_name=u'すくりーん',
                           access_token='this-is-access_token')
        res = app.get('/auth/oauth_callback')


        self.assertEqual(res.location, 'http://localhost/')

    def test_operator_list(self):
        app = _getTarget()
        app.get('/auth/operator/')

    def test_operator(self):
        app = _getTarget()


    def test_role_list(self):
        app = _getTarget()
        
        headers = _login_header('auth_tkt', test_settings['authtkt.secret'], 'fixture-user')
        res = app.get('/auth/role/', headers=headers)

    def test_role_get(self):
        app = _getTarget()
        permission_id = self._add_permission('my-permission')
        role_id = self._add_role(u"this-is-role")
        result = app.get('/auth/role/%d' % role_id)

        self.assertIn('my-permission', result.body)

        self._delete_role(u'this-is-role')
        self._delete_role(u'my-permission')

    def test_role_post(self):
        app = _getTarget()
        role_id = self._add_role(u"this-is-role")
        permission_id = self._add_permission('new-permission')
        
        params = {
            'permission': str(permission_id),
            }

        result = app.post('/auth/role/%d' % role_id, params=params)

        self.assertEqual(result.location, 'http://localhost/auth/role/%d' % role_id)
        self._delete_role(u'this-is-role')
        self._delete_permission(u'new-permission')


    def test_role_permission_list(self):

        app = _getTarget()
        role_id = self._add_role(u"this-is-role")
        app.get('/auth/role/%d/permission/' % role_id)
        self._delete_role(u'this-is-role')


    def test_role_permission(self):
        app = _getTarget()
        role_id = self._add_role('test-role')
        permission_id = self._add_permission('test-permission')
        rp_id = self._join_role_permission(role_id, permission_id)
        params = {'_method': 'delete'}

        result = app.post('/auth/role/%d/permission/%d' % (role_id, rp_id), params=params)
        
        self.assertEqual(result.location, 'http://localhost/auth/role/%d' % role_id)
        self._delete_role('test-role')
        self._delete_permission('test-permission')

        
    def _join_role_permission(self, role_id, permission_id):
        import sqlahelper
        from altaircms.auth.models import RolePermission
        rp = RolePermission(role_id=role_id, permission_id=permission_id)
        sqlahelper.get_session().add(rp)
        sqlahelper.get_session().flush()
        rp_id = rp.id
        import transaction
        transaction.commit()
        return rp_id

    def _add_permission(self, name):
        import sqlahelper
        from altaircms.auth.models import Permission
        permission = Permission(name=name)
        session = sqlahelper.get_session()
        session.add(permission)
        session.flush()
        permission_id = permission.id
        import transaction
        transaction.commit()
        return permission_id
        
    def _delete_permission(self, name):
        import sqlahelper
        from altaircms.auth.models import Permission
        Permission.query.filter(Permission.name==name).delete()
        import transaction
        transaction.commit()


    def _add_role(self, name):
        import sqlahelper
        from altaircms.auth.models import Role
        role = Role(name=name)
        session = sqlahelper.get_session()
        session.add(role)
        session.flush()
        role_id = role.id
        import transaction
        transaction.commit()

        return role_id

    def _delete_role(self, name):
        import sqlahelper
        from altaircms.auth.models import Role
        Role.query.filter(Role.name==name).delete()
        import transaction
        transaction.commit()

class FrontFunctionalTests(unittest.TestCase):

    # def test_front(self):
    #     app = _getTarget()
    #     page_name = 'test-page'
    #     url = 'page/one'
    #     page_id = self._add_page(page_name, url=url)
    #     res = app.get('/public/%s' % page_name)

    #     self._delete_page('page/one')

    # def test_front_to_preview(self):
    #     app = _getTarget()
    #     page_id = self._add_page('test-page')
    #     res = app.get('/to/preview/%d' % page_id)
    #     self._delete_page('test-page')

    # def test_front_preview(self):
    #     app = _getTarget()

    #     res = app.get('/')


    def _add_page(self, title, **kwargs):
        import sqlahelper
        from altaircms.page.models import Page
        page = Page(title=title, **kwargs)
        session = sqlahelper.get_session()
        session.add(page)
        session.flush()
        page_id = page.id
        import transaction
        transaction.commit()
        return page_id

    def _delete_page(self, title):
        from altaircms.page.models import Page
        Page.query.filter_by(title=title).delete()
        import transaction
        transaction.commit()

