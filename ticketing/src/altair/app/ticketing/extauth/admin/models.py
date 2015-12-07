import sqlalchemy as sa
from sqlalchemy import orm
from ..models import Base
from altair.models import Identifier

class Operator(Base):
    __tablename__ = 'Operator'
    id = sa.Column(Identifier, autoincrement=True, primary_key=True, nullable=False)
    organization_id = sa.Column(Identifier, sa.ForeignKey('Organization.id'), nullable=False)
    auth_identifier = sa.Column(sa.Unicode(128), unique=True, nullable=False)
    auth_secret = sa.Column(sa.Unicode(128), nullable=True)
    role = sa.Column(sa.Unicode(32), nullable=False)

    organization = orm.relationship('Organization', backref='operators')
