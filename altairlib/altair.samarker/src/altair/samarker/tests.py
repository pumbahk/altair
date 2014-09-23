import unittest

class SelectableMarkedClauseElementTest(unittest.TestCase):
    def _getTarget(self):
        from .expression import SelectableMarkedClauseElement
        return SelectableMarkedClauseElement

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_simple(self):
        from sqlalchemy.sql.expression import select
        from sqlalchemy.schema import Table, MetaData, Column
        from sqlalchemy.types import Integer
        meta = MetaData()
        table = Table(
            u'Foo',
            meta,
            Column(u'a', Integer())
            )
        target = self._makeOne(select([u'a'], from_obj=table), comment=u'test')
        result = target.compile()
        self.assertEqual(unicode(result).replace(u'\n', ''), u'SELECT a FROM "Foo" /* test */')

    def test_nested_from(self):
        from sqlalchemy.sql.expression import select
        from sqlalchemy.schema import Table, MetaData, Column
        from sqlalchemy.types import Integer
        meta = MetaData()
        table = Table(
            u'Foo',
            meta,
            Column(u'a', Integer())
            )
        target = self._makeOne(
            select(
                [u'a'],
                from_obj=self._makeOne(
                    select(
                        [u'a'],
                        from_obj=table,
                        ),
                    comment=u'inner'
                    )
                ),
            comment=u'test'
            )
        result = target.compile()
        self.assertEqual(unicode(result).replace(u'\n', ''), u'SELECT a FROM (SELECT a FROM "Foo") /* inner */ /* test */')

    def test_nested_in(self):
        from sqlalchemy.sql.expression import select
        from sqlalchemy.schema import Table, MetaData, Column
        from sqlalchemy.types import Integer
        meta = MetaData()
        table = Table(
            u'Foo',
            meta,
            Column(u'a', Integer())
            )
        target = self._makeOne(
            select(
                [u'a'],
                from_obj=table,
                whereclause=table.c.a.in_(
                    self._makeOne(
                        select(
                            [u'a'],
                            from_obj=table,
                            ),
                        comment=u'inner'
                        )
                    )
                ),
            comment=u'test'
            )
        result = target.compile()
        self.assertEqual(unicode(result).replace(u'\n', ''), u'SELECT a FROM "Foo" WHERE "Foo".a IN (SELECT a FROM "Foo") /* test */')

class MarkerQueryTest(unittest.TestCase):
    def _getTarget(self):
        from .orm import MarkerQuery
        return MarkerQuery

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def setUp(self):
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.types import Integer, Unicode
        from sqlalchemy.schema import Table, Column, ForeignKey, PrimaryKeyConstraint
        from sqlalchemy import create_engine

        self.Base = declarative_base()
        class Test(self.Base):
            __tablename__ = 'Test'
            id = Column(Integer, primary_key=True)
        self.Test = Test
        self.engine = create_engine('sqlite:///:memory:')
        self.Base.metadata.create_all(self.engine)

    def tearDown(self):
        self.Base.metadata.drop_all(self.engine)

    def test_it(self):
        from sqlalchemy.orm import sessionmaker
        from .orm import SessionFactoryFactory, MarkerQuery
        sessionmaker = SessionFactoryFactory(sessionmaker(bind=self.engine))
        session = sessionmaker()
        session.add(self.Test(id=1))
        session.commit()
        self.assertEqual(session.query(self.Test).first().id, 1)
        q = session.query(self.Test).filter_by(id=1)
        self.assertRegexpMatches(
            str(q).replace('\n', ''),
            r'''SELECT "Test".id AS "Test_id" FROM "Test" WHERE "Test".id = [^ ]+ /\* File "[^"]*", line \d+, in test_it \*/'''
            )

    def test_from_self(self):
        from sqlalchemy.orm import sessionmaker
        from .orm import SessionFactoryFactory, MarkerQuery
        sessionmaker = SessionFactoryFactory(sessionmaker(bind=self.engine))
        session = sessionmaker()
        session.add(self.Test(id=1))
        session.commit()
        q = session.query(self.Test).filter_by(id=1).from_self()
        self.assertRegexpMatches(
            str(q).replace('\n', ''),
            r'''SELECT anon_1."Test_id" AS "anon_1_Test_id" FROM \(SELECT "Test".id AS "Test_id" FROM "Test" WHERE "Test".id = [^ ]+\) AS anon_1 /\* File "[^"]*", line \d+, in test_from_self \*/'''
            )
