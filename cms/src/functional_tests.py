# -*- coding:utf-8 -*-

"""
機能テストはここでのみ行うこと
"""

import unittest
import webtest


test_settings = {
    "sqlalchemy.url": "sqlite:///",
    "sqlalchemy.echo": "true",
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

def _getTarget(store):
    from altaircms import main
    settings = test_settings.copy()
    settings['altaircms.asset.storepath'] = store
    app = main({}, **settings)
    import sqlahelper
    import transaction
    sqlahelper.get_base().metadata.drop_all()
    sqlahelper.get_base().metadata.create_all()
    from altaircms.auth.models import Role
    role = Role(name='administrator')
    session = sqlahelper.get_session()
    session.add(role)

    transaction.commit()

    return webtest.TestApp(app)




class BaseFunctionalTests(unittest.TestCase):


    def setUp(self):
        import tempfile
        self.store = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.store)


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
        app = _getTarget(self.store)

        res = app.get('/')

    def test_apikey_list_GET(self):
        app = _getTarget(self.store)

        res = app.get('/apikey/')

    def test_apikey_list_POST(self):
        app = _getTarget(self.store)

        res = app.post('/apikey/', params={'name': 'this-is-api-key'})

        self.assertEqual(res.location, 'http://localhost/apikey/')

    def test_apikey(self):

        app = _getTarget(self.store)
        id = self._add_api_key('this-is-api-key')
        res = app.post('/apikey/%d' % id, params={'_method': 'delete'})
        self._delete_api_key("this-is-api-key")

class AuthFunctionalTests(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.store = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.store)

    def test_login(self):
        app = _getTarget(self.store)
        app.get('/auth/login')

    def test_logout(self):
        app = _getTarget(self.store)
        app.get('/auth/logout')

    def test_oauth_entry(self):
        app = _getTarget(self.store)
        app.get('/auth/oauth')
    
    def test_oauth_callback(self):
        app = _getTarget(self.store)
        run_oauth_provider(user_id='this-is-user_id', 
                           screen_name=u'すくりーん',
                           access_token='this-is-access_token')
        res = app.get('/auth/oauth_callback')


        self.assertEqual(res.location, 'http://localhost/')

    def test_operator_list(self):
        app = _getTarget(self.store)
        app.get('/auth/operator/')

    def test_operator(self):
        app = _getTarget(self.store)


    def test_role_list(self):
        app = _getTarget(self.store)

        run_oauth_provider(user_id=999,
                           screen_name=u'すくりーん',
                           access_token='this-is-access_token')
        app.get('/auth/oauth_callback')
        app.get('/auth/role/')

    def test_role(self):
        app = _getTarget(self.store)
        role_id = self._add_role(u"this-is-role")
        app.get('/auth/role/%d' % role_id)
        self._delete_role(u'this-is-role')

    def test_role_permission_list(self):
        app = _getTarget(self.store)


    def test_role_permission(self):
        app = _getTarget(self.store)
        
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
