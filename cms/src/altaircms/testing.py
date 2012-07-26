from pyramid import testing
from sqlalchemy import create_engine
import transaction

import sqlahelper
from webob.multidict import MultiDict 
from pyramid.path import DottedNameResolver
from altaircms.models import Base

class DummyRequest(testing.DummyRequest):
    def __init__(self, *args, **kwargs):
        super(DummyRequest, self).__init__(*args, **kwargs)

        for attr in ("POST", "GET", "params"):
            if hasattr(self, attr):
                setattr(self, attr, MultiDict(getattr(self, attr)))

    def allowable(self, model, qs=None):
        return qs or model.query


def dummy_form_factory(name="DummyForm", validate=False, errors=None):
    def _validate(self):
        return validate

    def __init__(self, *args, **kwargs):
        self._args=args
        self._kwargs=kwargs

    attrs = dict(errors= errors or {"error1": "error-is-occured"}, 
                 validate = _validate, 
                 __init__=__init__)
    return type(name, (object, ), attrs)


def setup_db(models=[]):
    resolver = DottedNameResolver(package='altaircms')
    for m in models:
        resolver.maybe_resolve(m)

    engine = create_engine("sqlite:///")
    sqlahelper.get_session().remove()
    sqlahelper.add_engine(engine)
    sqlahelper.get_base().metadata.create_all()
    assert Base == sqlahelper.get_base()

def teardown_db():
    transaction.abort()
    sqlahelper.get_base().metadata.drop_all()


# from .dbinspect import listing_all
"""
todo: output meessage via logger
"""

def config():
    return testing.setUp(
        settings={"altaircms.plugin_static_directory": "altaircms:plugins/static", 
                  "altaircms.debug.strip_security": "true",
                  "altaircms.asset.storepath": "altaircms:../../data/assets", 
                  "sqlalchemy.url": "sqlite://", 
                  "widget.template_path_format": "%s.mako", 

                  "altair.oauth.client_id": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                  "altair.oauth.secret_key": "yyyyyyyyyyyyyyyyyyyyyyyyyyyyyy",
                  "altair.oauth.authorize_url": "http://localhost:7654/api/authorize",
                  "altair.oauth.access_token_url": "http://localhost:7654/api/access_token",

                  "altaircms.layout_directory": "."}
        )

def functionalTestSetUp(extra=None):
    setup_db(["altaircms.page.models", 
              "altaircms.tag.models", 
              "altaircms.event.models", 
              "altaircms.asset.models"])

    from altaircms import main
    defaults = {"sqlalchemy.url": "sqlite://", 
                "session.secret": "B7gzHVRUqErB1TFgSeLCHH3Ux6ShtI", 
                "mako.directories": "altaircms:templates", 
                "altaircms.asset.storepath": "altaircms:../../data/assets", 
                "altaircms.debug.strip_security": 'true', 
                "altaircms.plugin_static_directory": "altaircms:plugins/static", 
                "altaircms.logout.action": "altaircms.auth.api.LogoutSelfOnly", 

                "altair.oauth.client_id": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                "altair.oauth.secret_key": "yyyyyyyyyyyyyyyyyyyyyyyyyyyyyy",
                "altair.oauth.authorize_url": "http://localhost:7654/api/authorize",
                "altair.oauth.access_token_url": "http://localhost:7654/api/access_token",

                "altaircms.layout_directory": "."}
    config = defaults.copy()
    if extra:
        config.update(extra)
    app = main({}, **config)
    return app

def functionalTestTearDown():
    teardown_db()

