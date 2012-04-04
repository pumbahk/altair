import sys
import unittest
# from .dbinspect import listing_all
"""
todo: output meessage via logger
"""

from pyramid import testing

def _initTestingDB():
    from sqlalchemy import create_engine
    from altaircms.models import initialize_sql
    session = initialize_sql(create_engine('sqlite:///:memory:'))
    return session

def config():
    return testing.setUp(
        settings={"altaircms.plugin_static_directory": "altaircms:plugins/static", 
                  "widget.template_path_format": "%s.mako", 
                  "altaircms.layout_directory": "."}
        )

class BaseTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.session = _initTestingDB()


def _create_db(Base, DBSession, engine, force=True):
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

    from sqlalchemy import create_engine
    engine = create_engine('sqlite:///')
    engine.echo = echo
    if base is None or session is None:
        import altaircms.models as m
        return _create_db(m.Base, m.DBSession, engine, force)
    else:
        return _create_db(base, session, engine, force)


def dropall_db(base=None, session=None, message=None):
    if base is None or session is None:
        import altaircms.models as m
        # listing_all(m.Base.metadata)
        m.Base.metadata.drop_all(bind=m.DBSession.bind)
    else:
        # listing_all(base.metadata)
        base.metadata.drop_all(bind=session.bind)
