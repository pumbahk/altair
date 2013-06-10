from unittest import TestCase

class AnnotatedColumnTest(TestCase):
    def setUp(self):
        from . import AnnotatedColumn
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.types import Integer, Unicode
        from sqlalchemy.schema import Table, Column, ForeignKey, PrimaryKeyConstraint
        from sqlalchemy.orm import sessionmaker, relationship
        from sqlalchemy.ext.associationproxy import association_proxy
        from sqlalchemy import create_engine

        Base = declarative_base()
        class Test(Base):
            __tablename__ = 'Test'
            id = AnnotatedColumn(Integer, _annotations={'display_name':'Identifier'}, primary_key=True)
            first_name = AnnotatedColumn(Unicode, _a_display_name='First name')
            foo_ids = association_proxy('foos', 'id')

        class Foo(Base):
            __tablename__ = 'Foo'
            id = AnnotatedColumn(Integer, primary_key=True, _annotations={'display_name':'Foo #'})
            test_id = AnnotatedColumn(Integer, ForeignKey('Test.id'), primary_key=True, nullable=True, _a_display_name='Test #')
            test = relationship('Test', backref='foos')
            extra = Column(Unicode)

        Foo_Bar = Table(
            'Foo_Bar',
            Base.metadata,
            Column('foo_id', Integer, ForeignKey('Foo.id')),
            Column('bar_id', Integer, ForeignKey('Bar.id')),
            PrimaryKeyConstraint('foo_id', 'bar_id')
            )

        class Bar(Base):
            __tablename__ = 'Bar'
            id = AnnotatedColumn(Integer, primary_key=True, _a_display_name='Bar #')
            foos = relationship('Foo', backref='bars', secondary=Foo_Bar)

        self.Base = Base
        self.Test = Test
        self.Foo = Foo
        self.Bar = Bar
        self.Session = sessionmaker()
        self.engine = create_engine('sqlite:///:memory:')

    def test_basic(self):
        from sqlalchemy.sql.expression import insert, select, asc
        self.Base.metadata.create_all(self.engine)
        self.engine.execute(insert(self.Test.__table__).values([1, u'test1']))
        result = list(self.engine.execute(select([self.Test.__table__]).where("id=1")))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], 1)
        self.assertEqual(result[0][1], u'test1')

        session = self.Session(bind=self.engine)
        session.add(self.Test(id=2, first_name=u'test2', foos=[self.Foo(id=1, extra=u'1'), self.Foo(id=2, extra=u'2')]))
        session.add(self.Foo(id=3, bars=[self.Bar(id=1)]))
        session.flush()

        result = session.query(self.Test).order_by(asc(self.Test.id)).all()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].id, 1)
        self.assertEqual(result[0].first_name, u'test1')
        self.assertEqual(result[1].id, 2)
        self.assertEqual(result[1].first_name, u'test2')
        self.assertEqual([1, 2], result[1].foo_ids)

    def test_get_annotations_for(self):
        from . import get_annotations_for
        from sqlalchemy.orm.mapper import configure_mappers
        configure_mappers()
        self.assertEqual(get_annotations_for(self.Test.__table__.c.id), {'display_name': 'Identifier'})
        self.assertEqual(get_annotations_for(self.Test.id), {'display_name': 'Identifier'})
        self.assertEqual(get_annotations_for(self.Test.foos), {'display_name': 'Identifier'})
        self.assertEqual(get_annotations_for(self.Test.foo_ids), {'display_name': 'Foo #'})
        self.assertEqual(get_annotations_for(self.Foo.test), {'display_name': 'Test #'})
        self.assertEqual(get_annotations_for(self.Foo.bars), {'display_name': 'Bar #'})
        self.assertEqual(get_annotations_for(self.Bar.foos), {'display_name': 'Foo #'})
