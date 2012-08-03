import unittest

class LogicalDeletingOptionTests(unittest.TestCase):
    def _getTarget(self):
        from .logicaldeleting import LogicalDeletingOption
        return LogicalDeletingOption


    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)




    def test_process(self):
        import sqlalchemy as sa
        import sqlalchemy.orm as orm
        from sqlalchemy.ext.declarative import declarative_base
        session = orm.Session()
        metadata = sa.MetaData()
        engine = sa.create_engine("sqlite:///")
        session.bind = engine
        metadata.bind = engine

        Base = declarative_base(metadata=metadata)

        class User(Base):
            __tablename__ = 'users'
            id = sa.Column(sa.Integer, primary_key=True)
            deleted_at = sa.Column(sa.DateTime)

        class Address(Base):
            __tablename__ = 'addresses'

            id = sa.Column(sa.Integer, primary_key=True)
            deleted_at = sa.Column(sa.DateTime)
            user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
            user = orm.relationship('User', backref='addresses')

        metadata.create_all()

        target = self._makeOne("deleted_at")
        query = session.query(User).filter(Address.user_id==User.id)
        print query
        target._process(query)
        print query

        query = session.query(Address).filter(Address.user_id==User.id)
        print query
        target._process(query)
        print query

