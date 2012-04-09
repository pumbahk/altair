import sys
import unittest
# from .dbinspect import listing_all
"""
todo: output meessage via logger
"""
from sqlalchemy import create_engine
from altaircms.models import DBSession
from pyramid import testing
import transaction

def config():
    return testing.setUp(
        settings={"altaircms.plugin_static_directory": "altaircms:plugins/static", 
                  "altaircms.debug.strip_security": "true",
                  "widget.template_path_format": "%s.mako", 
                  "altaircms.layout_directory": "."}
        )

def functionalTestSetUp():
    DBSession.remove()
    create_db(force=False)

def functionalTestTearDown():
    transaction.abort()
    dropall_db(message="test view drop")
    create_db(force=True)

def _initTestingDB():
    from sqlalchemy import create_engine
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
    # listing_all(Base.metadata)
    return DBSession

def _message(message):
    if message:
        sys.stderr.write("----------------\n")
        sys.stderr.write(message)
        sys.stderr.write("\n----------------\n")

def create_db(echo=False, base=None, session=None, message=None, force=True):
    # _message(message)
    if base is None or session is None:
        engine = create_engine('sqlite:///')
        engine.echo = echo
        import altaircms.models as m
        return _create_db(m.Base, m.DBSession, engine, force)

    if force:
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
