import unittest

from ticketing.testing import _setup_db, _teardown_db
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String
from sqlalchemy.ext.declarative import declarative_base
import sqlahelper

class ModelUtilityTest(unittest.TestCase):
    def setUp(self):
        self.session = _setup_db()
        sqlahelper.set_base(declarative_base(self.session.bind))

    def tearDown(self):
        _teardown_db()
        sqlahelper.get_base().metadata.drop_all()
        sqlahelper.get_session().remove() 

    def test_record_to_appstruct(self):
        from ticketing.models import record_to_appstruct
        base = sqlahelper.get_base()

        class Foo(base):
            __tablename__ = 'foo'
            id = Column(Integer, primary_key=True)
            string = Column(String(255))
            bars = relationship(lambda:Bar, backref='foo')
            bazs = relationship(lambda:Baz, backref='foo')

        class Bar(base):
            __tablename__ = 'bar'
            id = Column(Integer, primary_key=True)
            foo_id = Column(Integer, ForeignKey(Foo.id))

        class Baz(base):
            __tablename__ = 'baz'
            id = Column(Integer, primary_key=True)
            foo_id = Column(Integer, ForeignKey(Foo.id))

        base.metadata.drop_all()
        base.metadata.create_all()

        foo = Foo(
            id=1,
            string='aa',
            bars=[
                Bar(id=1),
                Bar(id=2)
                ],
            bazs=[
                Baz(id=1),
                Baz(id=2)
                ]
            )
        self.assertEqual(
            {
                'id': 1,
                'string': 'aa'
                },
            record_to_appstruct(foo)
            )
        self.session.add(foo)
        self.session.flush()
        self.assertEqual(
            {
                'id': 1,
                'string': 'aa'
                },
            record_to_appstruct(foo)
            )

    def test_BaseModel_clone(self):
        from ticketing.models import BaseModel
        base = sqlahelper.get_base()

        class Mixin1(object):
            __clone_excluded__ = ['mixin1']
            mixin1 = Column(String(255))

        class Mixin2(object):
            mixin2 = Column(String(255))

        class Foo(base, BaseModel, Mixin1, Mixin2):
            __tablename__ = 'foo'
            id = Column(Integer, primary_key=True)
            string = Column(String(255))
            bars = relationship(lambda:Bar, backref='foo')
            bazs = relationship(lambda:Baz, backref='foo')

        class Bar(base, BaseModel):
            __tablename__ = 'bar'
            id = Column(Integer, primary_key=True)
            foo_id = Column(Integer, ForeignKey(Foo.id))

        class Baz(base, BaseModel):
            __tablename__ = 'baz'
            id = Column(Integer, primary_key=True)
            foo_id = Column(Integer, ForeignKey(Foo.id))

        foo = Foo(
            id=1,
            string='aa',
            mixin1='bb',
            mixin2='cc',
            bars=[
                Bar(id=1),
                Bar(id=2)
                ],
            bazs=[
                Baz(id=1),
                Baz(id=2)
                ]
            )

        shallow_foo = Foo.clone(foo)
        self.assertEqual('aa', shallow_foo.string)
        self.assertEqual(None, shallow_foo.mixin1)
        self.assertEqual('cc', shallow_foo.mixin2)
        self.assertEqual(0, len(shallow_foo.bars))
        self.assertEqual(0, len(shallow_foo.bazs))
        deep_foo = Foo.clone(foo, True)
        self.assertEqual('aa', deep_foo.string)
        self.assertEqual(None, deep_foo.mixin1)
        self.assertEqual('cc', deep_foo.mixin2)
        self.assertEqual(2, len(deep_foo.bars))
        self.assertEqual(2, len(deep_foo.bazs))

