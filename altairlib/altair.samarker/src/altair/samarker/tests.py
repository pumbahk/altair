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

    def test_union(self):
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
                whereclause=(table.c.a == 1)
                ),
            comment=u'test'
            )
        target = target.union(
            select(
                [u'a'],
                from_obj=table,
                whereclause=(table.c.a == 2)
                )
            )
        result = target.compile()
        self.assertRegexpMatches(unicode(result).replace(u'\n', ''), ur'SELECT a FROM "Foo" WHERE "Foo".a = [^ ]+ UNION SELECT a FROM "Foo" WHERE "Foo".a = [^ ]+ /\* test \*/')


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
        from sqlalchemy.orm import relationship
        from sqlalchemy import create_engine

        self.Base = declarative_base()
        class Test1(self.Base):
            __tablename__ = 'Test1'
            id = Column(Integer, primary_key=True)
        class Test2(self.Base):
            __tablename__ = 'Test2'
            id = Column(Integer, primary_key=True)
            test1_id = Column(Integer, ForeignKey('Test1.id'))
            test1 = relationship(Test1, backref='test2_list')
        self.Test1 = Test1
        self.Test2 = Test2
        self.engine = create_engine('sqlite:///:memory:')
        self.Base.metadata.create_all(self.engine)

    def tearDown(self):
        self.Base.metadata.drop_all(self.engine)

    def test_it(self):
        from sqlalchemy.orm import sessionmaker
        from .orm import SessionFactoryFactory, MarkerQuery
        sessionmaker = SessionFactoryFactory(sessionmaker(bind=self.engine))
        session = sessionmaker()
        session.add(self.Test1(id=1))
        session.commit()
        self.assertEqual(session.query(self.Test1).first().id, 1)
        q = session.query(self.Test1).filter_by(id=1)
        self.assertRegexpMatches(
            str(q).replace('\n', ''),
            r'''SELECT "Test1".id AS "Test1_id" FROM "Test1" WHERE "Test1".id = [^ ]+ /\* File "[^"]*", line \d+, in test_it \*/'''
            )

    def test_from_self(self):
        from sqlalchemy.orm import sessionmaker
        from .orm import SessionFactoryFactory, MarkerQuery
        sessionmaker = SessionFactoryFactory(sessionmaker(bind=self.engine))
        session = sessionmaker()
        session.add(self.Test1(id=1))
        session.commit()
        q = session.query(self.Test1).filter_by(id=1).from_self()
        self.assertRegexpMatches(
            str(q).replace('\n', ''),
            r'''SELECT anon_1."Test1_id" AS "anon_1_Test1_id" FROM \(SELECT "Test1".id AS "Test1_id" FROM "Test1" WHERE "Test1".id = [^ ]+\) AS anon_1 /\* File "[^"]*", line \d+, in test_from_self \*/'''
            )

    def test_subquery(self):
        from sqlalchemy.orm import sessionmaker
        from .orm import SessionFactoryFactory, MarkerQuery
        plain_session_maker = sessionmaker(bind=self.engine)
        sessionmakers = [plain_session_maker, SessionFactoryFactory(plain_session_maker)]
        def doit(session):
            session.add(self.Test1(id=1, test2_list=[self.Test2()]))
            q1 = session.query(self.Test1.id.label('FOO')).join(self.Test1.test2_list).filter_by(id=1).subquery()
            try:
                q2 = session.query(q1.c.FOO)
            except:
                self.fail('%r: %s' % (session, type(q1)))
            self.assertEqual([(1,)], q2.all())
            session.rollback()
        for _sessionmaker in sessionmakers:
            doit(_sessionmaker())

    def test_delete_1(self):
        from sqlalchemy.orm import sessionmaker
        from .orm import SessionFactoryFactory, MarkerQuery
        plain_session_maker = sessionmaker(bind=self.engine)
        sessionmakers = [plain_session_maker, SessionFactoryFactory(plain_session_maker)]
        def doit(session):
            session.add(self.Test1(id=1, test2_list=[self.Test2()]))
            q = session.query(self.Test1).filter_by(id=1)
            try:
                q.delete()
            except Exception as e:
                self.fail('%r: %s - %s' % (session, e, q))
            session.rollback()
        for _sessionmaker in sessionmakers:
            doit(_sessionmaker())

    def test_delete_2(self):
        from sqlalchemy.orm import sessionmaker
        from .orm import SessionFactoryFactory, MarkerQuery
        plain_session_maker = sessionmaker(bind=self.engine)
        sessionmakers = [plain_session_maker, SessionFactoryFactory(plain_session_maker)]
        def doit(session):
            session.add(self.Test1(id=1, test2_list=[self.Test2()]))
            q = session.query(self.Test1).filter_by(id=1)
            try:
                q.delete('fetch')
            except Exception as e:
                self.fail('%r: %s - %s' % (session, e, q))
            session.rollback()
        for _sessionmaker in sessionmakers:
            doit(_sessionmaker())


