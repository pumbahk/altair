# -*- coding:utf-8 -*-

"""
機能テストはここでのみ行うこと
"""

import unittest
import webtest

def paste_fixture(event):
    fixture_values = dict(event)
    request = event['request']
    if 'paste.testing' in request.environ:
        request.environ['paste.testing_variables']['render_event'] = fixture_values
        

def includeme(config):
    config.add_subscriber(paste_fixture,
                          'pyramid.events.BeforeRender')

class BaseFunctionalTests(unittest.TestCase):
    settings = {
        "sqlalchemy.url": "sqlite:///",
        #"altaircms.asset.storepath": "%(here)s/data/assets" % here,
        "altaircms.debug.strip_security": True,
        "altaircms.layout_directory": "altaircms:templates/front/layout",
        "altaircms.plugin_static_directory":  "altaircms:plugins/static",
        "authtkt.secret": 'authtkt-secret',
        "session.secret": 'session-secret',
        "pyramid.includes": __name__,
        }


    def setUp(self):
        import tempfile
        self.store = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.store)

    def _getTarget(self):
        from altaircms import main
        settings = self.settings.copy()
        settings['altaircms.asset.storepath'] = self.store
        app = main({}, **settings)
        import sqlahelper
        sqlahelper.get_base().metadata.drop_all()
        sqlahelper.get_base().metadata.create_all()
        return webtest.TestApp(app)

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
        session = sqlahelper.get_session()
        APIKey.query.filter(APIKey.name==name).delete()
        import transaction
        transaction.commit()




    def test_dashboard(self):
        app = self._getTarget()

        res = app.get('/')

    def test_apikey_list_GET(self):
        app = self._getTarget()

        res = app.get('/apikey/')

    def test_apikey_list_POST(self):
        app = self._getTarget()

        res = app.post('/apikey/', params={'name': 'this-is-api-key'})

        self.assertEqual(res.location, 'http://localhost/apikey/')

    def test_apikey(self):

        app = self._getTarget()
        id = self._add_api_key('this-is-api-key')
        res = app.post('/apikey/%d' % id, params={'_method': 'delete'})
        self._delete_api_key("this-is-api-key")
