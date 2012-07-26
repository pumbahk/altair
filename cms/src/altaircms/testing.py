from pyramid import testing
from webob.multidict import MultiDict 

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
    from pyramid.path import DottedNameResolver
    resolver = DottedNameResolver(package='altaircms')
    for m in models:
        resolver.maybe_resolve(m)

    import sqlahelper
    from sqlalchemy import create_engine
    engine = create_engine("sqlite:///")
    sqlahelper.get_session().remove()
    sqlahelper.add_engine(engine)
    sqlahelper.get_base().metadata.create_all()
    from ..models import Base
    assert Base == sqlahelper.get_base()

def teardown_db():
    import transaction
    transaction.abort()
    import sqlahelper
    sqlahelper.get_base().metadata.drop_all()

import sys
import unittest
# from .dbinspect import listing_all
"""
todo: output meessage via logger
"""
from sqlalchemy import create_engine
from altaircms.models import DBSession
from altaircms.models import Base
from pyramid import testing
import transaction

def db_initialize_for_unittest(echo=False):
    import sqlalchemy as sa
    engine = sa.create_engine("sqlite://", echo=echo)
    Base.metadata.bind = engine
    DBSession.configure(bind=engine)
    Base.metadata.create_all()
    unittest.main()

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
    DBSession.remove()
    import sqlahelper

    engine = create_engine("sqlite:///")
    engine.echo = False
    sqlahelper.get_session().remove()
    sqlahelper.add_engine(engine)

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

    sqlahelper.get_base().metadata.drop_all()
    sqlahelper.get_base().metadata.create_all()
    return app

def functionalTestTearDown():
    dropall_db(message="test view drop")
    create_db(force=True)
    transaction.abort()
    testing.tearDown()

def _initTestingDB():
    DBSession.remove()
    from altaircms.models import initialize_sql
    engine = create_engine('sqlite:///:memory:')
    # engine.echo = True
    import sqlahelper

    sqlahelper.add_engine(engine)
    session = initialize_sql(engine, dropall=True)
    return session

class BaseTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.session = _initTestingDB()

def _create_db(Base, DBSession, engine, force=False):
    if force or any([x.bind is None for x in [Base.metadata, DBSession]]):
        if not Base.metadata.is_bound():
            Base.metadata.bind = engine
        if not DBSession.bind and not DBSession.registry.has():
            DBSession.configure(bind=engine)
        Base.metadata.create_all()
    return DBSession

def _message(message):
    if message:
        sys.stderr.write("----------------\n")
        sys.stderr.write(message)
        sys.stderr.write("\n----------------\n")

def create_db(echo=False, base=None, session=None, message=None, force=False):
    # _message(message)
    if base is None or session is None:
        engine = create_engine('sqlite:///')
        engine.echo = echo
        import altaircms.models as m
        return _create_db(m.Base, m.DBSession, engine, force)
    else:
        engine = create_engine('sqlite:///')
        engine.echo = echo
        return _create_db(base, session, engine, force)

def dropall_db(base=None, session=None, message=None):
    if base is None or session is None:
        import altaircms.models as m
        # listing_all(m.Base.metadata)
        m.Base.metadata.drop_all(bind=m.DBSession.bind)
    else:
        # listing_all(base.metadata)
        base.metadata.drop_all(bind=session.bind)
