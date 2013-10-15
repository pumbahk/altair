# -*- coding:utf-8 -*-
import unittest
import transaction
import sqlalchemy as sa
from .testing import (
    swap_engine, 
)

_engine = None
def setUpModule():
    from altair.app.ticketing.core.models import Base
    from altair.app.ticketing.core.models import DBSession
    import sqlahelper
    try:
        engine__ = sqlahelper.get_engine()
    except RuntimeError:
        engine__ = sa.create_engine("sqlite://", echo=False)
        sqlahelper.add_engine(engine__)
        Base = sqlahelper.get_base()
        assert Base.metadata.bind == sqlahelper.get_engine()
        Base.metadata.create_all()
    print "engine__", id(engine__)
    from altair.app.ticketing.core.models import Organization
    DBSession.add(Organization(id=1000000000, name="dummy", short_name="dummy"))
    transaction.commit()
    print Organization.query.filter_by(name="dummy").count()
    assert Organization.query.filter_by(name="dummy").count() == 1

    global _engine
    from altair.app.ticketing.models import Base
    engine = sa.create_engine("sqlite://", echo=False)
    _engine = swap_engine(engine)
    print "_engine", id(_engine)
    print "engine", id(engine)
    assert engine__ != engine
    assert Base.metadata.bind == engine
    Base.metadata.create_all()
    print Organization.query.filter_by(name="dummy").count()
    assert Organization.query.filter_by(name="dummy").count() == 0
    
def tearDownModule():
    global _engine
    swap_engine(_engine)
    from altair.app.ticketing.models import DBSession
    from altair.app.ticketing.core.models import Organization
    assert Organization.query.filter_by(name="dummy").count() == 1


class Tests(unittest.TestCase):
    def tearDown(self):
        transaction.abort()

    def test_it(self):
        from .testing import get_ordered_product_item__full_relation
        from altair.app.ticketing.models import DBSession
        get_ordered_product_item__full_relation(quantity=2, quantity_only=True)
        DBSession.flush()
        
