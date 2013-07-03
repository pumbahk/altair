from sqlalchemy import (
    Column,
    Integer,
    create_engine,
)
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
DBSession = scoped_session(sessionmaker())

def setUpDB():
    engine = create_engine("sqlite:///")
    DBSession.remove()
    DBSession.configure(bind=engine)
    Base.metadata.create_all(bind=DBSession.bind)
    return DBSession

def tearDownDB():
    DBSession.rollback()
    DBSession.remove()


class Testing(Base):
    __tablename__ = 'testing'
    query = DBSession.query_property()
    id = Column(Integer, primary_key=True)
    value = Column(Integer)

class DummyHandler(object):
    def __init__(self, return_value, query_times=10):
        self.called = []
        self.return_value = return_value
        self.query_times = query_times

    def __call__(self, request):
        self.called.append(request)
        results = []
        for i in range(self.query_times):
            results.append(Testing.query.all())
        request.environ['altair.queryprofile.testing.results'] = results
        return self.return_value

