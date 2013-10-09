from pyramid import testing
from sqlalchemy import create_engine
import transaction

import sqlahelper
from webob.multidict import MultiDict 
from pyramid.path import DottedNameResolver
from altaircms.models import Base
from pyramid.decorator import reify
import StringIO

class DummyFileStorage(object):
    def __init__(self, filename, _file="", file=None):
        self.filename = filename
        if file:
            self.file = open(file)
        else:
            self.file = StringIO.StringIO(_file)

class DummyRequest(testing.DummyRequest):
    def __init__(self, *args, **kwargs):
        super(DummyRequest, self).__init__(*args, **kwargs)
        for attr in ("POST", "GET", "params"):
            if hasattr(self, attr):
                setattr(self, attr, MultiDict(getattr(self, attr)))

    def allowable(self, model, qs=None):
        return qs or model.query

class ExtDummyRequest(DummyRequest):
    def __init__(self, *args, **kwargs):
        super(ExtDummyRequest, self).__init__(*args, **kwargs)
        if "organization_id" in kwargs:
            self.organization_id = kwargs["organization_id"]
        if "operator_id" in kwargs:
            from altaircms.auth.models import Operator
            self.user = Operator.query.filter_by(id=kwargs["operator_id"]).first()
            assert unicode(self.user.organization_id) == unicode(self.organization_id)

        if "current_request" in kwargs and kwargs["current_request"]:
            from pyramid.threadlocal import manager
            from pyramid.registry import global_registry
            manager.push({"request": self, "registry": getattr(self, "registry", global_registry)})
        if "referrer" in kwargs:
            self.referrer = kwargs["referrer"]
        else:
            self.referrer = "/"

    @reify
    def organization(self):
        from altaircms.auth.models import Organization
        if self.organization_id is None:
            return None
        return Organization.query.filter_by(id=self.organization_id).first()

    def allowable(self, model, qs=None):
        from altaircms.auth.api import get_allowable_query
        return get_allowable_query(self)(model, qs=qs)


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


def setup_db(models=[], extra_tables=[]):
    base =  sqlahelper.get_base()
    sqlahelper.get_session().remove()

    resolver = DottedNameResolver()
    for m in models:
        resolver.maybe_resolve(m)

    metadata = base.metadata
    for t in extra_tables:
        t.tometadata(metadata)

    engine = create_engine("sqlite:///")
    sqlahelper.add_engine(engine)
    base.metadata.create_all()
    assert Base == sqlahelper.get_base()

def teardown_db(base=None):
    transaction.abort()
    base = base or sqlahelper.get_base()
    base.metadata.drop_all()

"""
todo: output meessage via logger
"""

def config():
    return testing.setUp(
        settings={"altaircms.plugin_static_directory": "altaircms:plugins/static", 
                  "altaircms.debug.strip_security": "true",
                  "altaircms.asset.storepath": "altaircms:../../data/assets", 
                  "sqlalchemy.url": "sqlite://", 
                  "widget.template_path_format": "%s.html", 

                  "altair.oauth.client_id": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                  "altair.oauth.secret_key": "yyyyyyyyyyyyyyyyyyyyyyyyyyyyyy",
                  "altair.oauth.authorize_url": "http://localhost:7654/api/authorize",
                  "altair.oauth.access_token_url": "http://localhost:7654/api/access_token",

                  "altaircms.layout_directory": "."}
        )

def functionalTestSetUp(extra=None):
    setup_db(["altaircms.page.models", 
              "altaircms.tag.models", 
              "altaircms.widget.models", 
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
                'altaircms.organization.mapping.json': "altaircms:../../organization.json", 
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

