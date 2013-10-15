# -*- coding:utf-8 -*-
from ..testing import DummyRequest
import sqlalchemy as sa
_engine = None

def setUpSwappedDB():
    from altair.app.ticketing.core.models import Base
    import sqlahelper
    try:
        engine__ = sqlahelper.get_engine()
    except RuntimeError:
        engine__ = sa.create_engine("sqlite://", echo=False)
        sqlahelper.add_engine(engine__)
        assert Base.metadata.bind == sqlahelper.get_engine()
        Base.metadata.create_all()
    global _engine
    from altair.app.ticketing.models import Base
    engine = sa.create_engine("sqlite://", echo=False)
    _engine = swap_engine(engine)
    assert engine__ != engine
    assert Base.metadata.bind == engine
    Base.metadata.create_all()

def tearDownSwappedDB():
    global _engine
    swap_engine(_engine)


def set_default_engine(engine, name="default"):
    "i hate sqlahelper"
    import sqlahelper
    sqlahelper._engines[name] = engine

def swap_engine(engine):
    import sqlahelper
    from altair.app.ticketing.core.models import DBSession
    base = sqlahelper.get_base()
    old_engine = sqlahelper.get_engine()

    session = sqlahelper.get_session()
    assert session == DBSession
    session.remove()

    assert old_engine == session.bind == base.metadata.bind
    set_default_engine(engine)
    base.metadata.bind = engine
    session.configure(bind=engine)
    session.bind = engine ## xxx: used by DBSession.query_property. but, session.configure() not changes this attributes.
    assert engine == base.metadata.bind
    assert engine == session.bind
    return old_engine

