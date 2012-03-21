
import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.ext.declarative import declarative_base

metadata = sa.MetaData()
Base = declarative_base()
DBSession = orm.scoped_session(orm.sessionmaker())

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
