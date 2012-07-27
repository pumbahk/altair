from ...models import DBSession, Base, WithTimestamp, Identifier
from ...core.models import Organization
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String, DateTime
from zope.interface import implementer

class APIKey(Base, WithTimestamp):
    __tablename__ = 'APIKey'
    query = DBSession.query_property()

    def generate_key(self):
        from uuid import uuid4
        import hashlib

        hash = hashlib.new('sha256', str(uuid4()))
        return hash.hexdigest()

    id = Column(Integer, primary_key=True)
    expire_at = Column(DateTime, nullable=True)
    apikey = Column(String(255), nullable=False, unique=True, default=generate_key)
