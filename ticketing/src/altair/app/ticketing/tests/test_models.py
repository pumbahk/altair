import unittest

from altair.app.ticketing.testing import _setup_db, _teardown_db
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String
from sqlalchemy.ext.declarative import declarative_base
import sqlahelper

class ModelUtilityTest(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        from altair.app.ticketing.core.models import Base
        sqlahelper.set_base(Base)

    def setUp(self):
        self.session = _setup_db()
        sqlahelper.set_base(declarative_base(self.session.bind))

    def tearDown(self):
        _teardown_db()
        sqlahelper.get_base().metadata.drop_all()
        sqlahelper.get_session().remove() 

    def test_record_to_appstruct(self):
        from altair.app.ticketing.models import record_to_appstruct
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
        from altair.app.ticketing.models import BaseModel
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

class CSVRendererTest(unittest.TestCase):
    def testDereference(self):
        from altair.app.ticketing.utils import dereference
        from datetime import date
        self.assertEqual(123, dereference({u'a':123}, u'a'))
        self.assertEqual(123, dereference({u'a':{u'b':123}}, u'a[b]'))
        self.assertEqual(2000, dereference({u'a':date(2000, 1, 2)}, u'a.year'))
        self.assertEqual(1, dereference({u'a':date(2000, 1, 2)}, u'a.month'))
        self.assertEqual(2, dereference({u'a':date(2000, 1, 2)}, u'a.day'))

    def testPlainTextRenderer(self):
        from altair.app.ticketing.csvutils import PlainTextRenderer, CSVRenderer
        renderer = CSVRenderer([
            PlainTextRenderer(u'a'),
            PlainTextRenderer(u'b'),
            ])
        renderer.append({u'a':123, u'b':456})
        self.assertEqual([[u'a', u'b'], [u'123', u'456']], list(renderer.render()))

    def testCollectionRenderer(self):
        from altair.app.ticketing.csvutils import PlainTextRenderer, CollectionRenderer, CSVRenderer
        renderer = CSVRenderer([
            PlainTextRenderer(u'a'),
            PlainTextRenderer(u'b'),
            CollectionRenderer(
                u'c',
                u'c',
                [
                    PlainTextRenderer(u'c[a]'),
                    PlainTextRenderer(u'c[b]')
                    ]
                )
            ])
        renderer.append({
            u'a': 123,
            u'b': 456,
            u'c': [
                {u'a': 789, u'b': 123},
                {u'a': 456, u'b': 789}
                ]
            })
        renderer.append({
            u'a': 'aaa',
            u'b': 'bbb',
            u'c': [
                {u'a': 123, u'b': 456},
                ]
            })
        self.assertEqual([
            [u'a', u'b', u'c[a][0]', u'c[b][0]', u'c[a][1]', u'c[b][1]'],
            [u'123', u'456', u'789', u'123', u'456', u'789'],
            [u'aaa', u'bbb', u'123', u'456', u'', u''],
            ],
            list(renderer.render())
            )

    def testLocalizedRendering(self):
        from altair.app.ticketing.csvutils import PlainTextRenderer, CollectionRenderer, CSVRenderer
        renderer = CSVRenderer([
            PlainTextRenderer(u'a'),
            PlainTextRenderer(u'b'),
            CollectionRenderer(
                u'c',
                u'c',
                [
                    PlainTextRenderer(u'c[a]'),
                    PlainTextRenderer(u'c[b]')
                    ]
                )
            ])
        renderer.append({
            u'a': 123,
            u'b': 456,
            u'c': [
                {u'a': 789, u'b': 123},
                {u'a': 456, u'b': 789}
                ]
            })
        localized_columns = {
            u'a': u'AAA',
            u'b': u'BBB',
            u'c[a]': u'CCC-a',
            u'c[b]': u'CCC-b',
            }
        self.assertEqual([
            [u'AAA', u'BBB', u'CCC-a[0]', u'CCC-b[0]', u'CCC-a[1]', u'CCC-b[1]'],
            [u'123', u'456', u'789', u'123', u'456', u'789'],
            ],
            list(renderer.render(localized_columns))
            )

    def testComplicated(self):
        from altair.app.ticketing.csvutils import PlainTextRenderer, CollectionRenderer, AttributeRenderer, CSVRenderer
        renderer = CSVRenderer([
            PlainTextRenderer(u'a'),
            PlainTextRenderer(u'b'),
            CollectionRenderer(
                u'c',
                u'c',
                [
                    AttributeRenderer(u'c', 'c'),
                    ]
                ),
            CollectionRenderer(
                u'd',
                u'd',
                [
                    CollectionRenderer(u'd', 'd', [
                        PlainTextRenderer(u'd[a]'),
                        ]),
                    ]
                )
            ])
        renderer.append({
            u'a': 123,
            u'b': 456,
            u'c': [
                {u'a': 789, u'b': 123},
                {u'a': 456, u'b': 789}
                ],
            u'd': [
                [
                    { 'a': 123 }, 
                    { 'a': 456 }, 
                    { 'a': 789 }, 
                    ]
                ]
            })
        self.assertEqual([
            [u'a', u'b', u'c[a][0]', u'c[b][0]', u'c[a][1]', u'c[b][1]', u'd[a][0][0]', u'd[a][0][1]', u'd[a][0][2]'],
            [u'123', u'456', u'789', u'123', u'456', u'789', u'123', u'456', u'789'],
            ],
            list(renderer.render())
            )


