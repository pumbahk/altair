# coding: utf-8
import sqlalchemy as sa
from pyramid.decorator import reify
import sqlalchemy.orm as orm
from altaircms.models import Base, BaseOriginalMixin
from altaircms.models import WithOrganizationMixin
from altaircms.models import DBSession
from altaircms.models import Word, Event_Word
from altaircms.auth.models import Organization
from datetime import datetime
from datetime import timedelta
from altaircms.models import Genre
from altaircms.page.models import Page, PageSet


class Artist(BaseOriginalMixin, WithOrganizationMixin, Base):
    """
    アーティスト
    """
    __tablename__ = "artist"
    query = DBSession.query_property()

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.Unicode(255))
    kana = sa.Column(sa.Unicode(255))
    code = sa.Column(sa.Unicode(255))
    url = sa.Column(sa.Unicode(255))
    image = sa.Column(sa.Unicode(255))
    providers = sa.orm.relationship('Provider', backref='artist', uselist=True, cascade='all')
    description = sa.Column(sa.Unicode(255))
    public = sa.Column(sa.Boolean, default=False)
    organization_id = sa.Column(sa.Unicode(255))
    display_order = sa.Column(sa.Integer, default=50)

    @reify
    def organization(self):
        return Organization.query.filter_by(id=self.organization_id).one()


class Provider(BaseOriginalMixin, WithOrganizationMixin, Base):
    """
    SNSプロバイダー
    """
    __tablename__ = "provider"
    query = DBSession.query_property()

    id = sa.Column(sa.Integer, primary_key=True)
    artist_id = sa.Column(sa.Integer, sa.ForeignKey('artist.id'))
    provider_type = sa.Column(sa.Unicode(255))
    service_id = sa.Column(sa.Unicode(255))
