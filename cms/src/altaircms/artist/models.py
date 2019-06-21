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
    イベント
    """
    __tablename__ = "artist"
    query = DBSession.query_property()

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.Unicode(255))
    kana = sa.Column(sa.Unicode(255))
    code = sa.Column(sa.Unicode(255))
    url = sa.Column(sa.Unicode(255))
    image = sa.Column(sa.Unicode(255))
    description = sa.Column(sa.Unicode(255))
    public = sa.Column(sa.Boolean, default=False)
    organization_id = sa.Column(sa.Unicode(255))

    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now)

    @reify
    def organization(self):
        return Organization.query.filter_by(id=self.organization_id).one()
