import sqlalchemy as sa

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class Host(Base):
    __tablename__ = 'host'
    organization_id = sa.Column(sa.Integer, primary_key=True)
    id = sa.Column(sa.Integer)
    host_name = sa.Column(sa.Unicode(255), primary_key=True)

    def __init__(self, organization_id, id, host_name):
        self.organization_id = organization_id
        self.id = id
        self.host_name = host_name

