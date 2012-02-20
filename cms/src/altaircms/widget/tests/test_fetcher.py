import unittest
import sqlalchemy as sa
from altaircms.models import Base as DefaultBase
import sqlalchemy.orm as orm

class Base(DefaultBase):
    __abstract__ = True
    metadata = sa.MetaData()

DBSession = orm.scoped_session(orm.sessionmaker())
DBSession.remove()
class DummyWidget(Base):
    __tablename__ = "dummy"
    def __init__(self, id=None, asset_id=None):
        self.id = id
        self.asset_id = asset_id
    query = DBSession.query_property()
    id = sa.Column(sa.Integer, primary_key=True)
    asset_id = sa.Column(sa.Integer)
    
from altaircms.widget.fetcher import WidgetFetcher
WidgetFetcher.add_fetch_method("dummy_widget", DummyWidget)

def setUpModule():
    from altaircms.testutils import create_db
    create_db(base=Base, session=DBSession)

def tearDownModule():
    from altaircms.testutils import dropall_db
    dropall_db(base=Base, session=DBSession)


class WidgetFetcherTest(unittest.TestCase):
    def tearDown(self):
        import transaction
        transaction.abort()

    def _getSession(self):
        return DBSession

    def _getTarget(self, session):
        from altaircms.widget.fetcher import WidgetFetcher
        return WidgetFetcher(session=session)

    def test_dummy_widget(self):
        session = self._getSession()
        iw = DummyWidget(id=1, asset_id=1)
        session.add(iw)
        
        fetcher = self._getTarget(session)
        self.assertEquals(fetcher.fetch("dummy_widget", [1]).one().asset_id, 1)
        self.assertEquals(fetcher.dummy_widget([1]).one().asset_id, 1)

    def test_not_found_widget(self):
        session = self._getSession()
        iw = DummyWidget(id=1, asset_id=1)
        session.add(iw)
        
        fetcher = self._getTarget(session)
        from altaircms.widget.fetcher import WidgetFetchException
        self.assertRaises(WidgetFetchException, 
            lambda : fetcher.fetch("not_found_widget", [1]).one().asset_id)

if __name__ == "__main__":
    unittest.main()
