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

def db_initialize_for_unittest():
    import sqlalchemy as sa
    engine = sa.create_engine("sqlite://")
    Base.metadata.bind = engine
    DBSession.configure(bind=engine)
    Base.metadata.create_all()
    unittest.main()

def config():
    return testing.setUp(
        settings={"altaircms.plugin_static_directory": "altaircms:plugins/static", 
                  "altaircms.debug.strip_security": "true",
                  "sqlalchemy.url": "sqlite://", 
                  "widget.template_path_format": "%s.mako", 
                  "altaircms.layout_directory": "."}
        )

def functionalTestSetUp(extra=None):
    DBSession.remove()
    from altaircms import main
    defaults = {"sqlalchemy.url": "sqlite://", 
                "session.secret": "B7gzHVRUqErB1TFgSeLCHH3Ux6ShtI", 
                "mako.directories": "altaircms:templates", 
                "altaircms.debug.strip_security": 'true', 
                "altaircms.plugin_static_directory": "altaircms:plugins/static", 
                "altaircms.layout_directory": "."}
    config = defaults.copy()
    if extra:
        config.update(extra)
    app = main({}, **config)
    # create_db(force=False)
    Base.metadata.create_all()
    return app

def functionalTestTearDown():
    dropall_db(message="test view drop")
    create_db(force=True)
    transaction.abort()

def _initTestingDB():
    from altaircms.models import initialize_sql
    session = initialize_sql(create_engine('sqlite:///:memory:'))
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
