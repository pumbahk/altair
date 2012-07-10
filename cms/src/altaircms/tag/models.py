
import sqlalchemy as sa
import sqlalchemy.orm as orm
import sqlalchemy.schema as saschema
from altaircms.models import Base
from altaircms.models import DBSession

from datetime import datetime
from altaircms.page.models import Page
from altaircms.models import WithOrganizationMixin

class PageTag2Page(Base):
    __tablename__ = "pagetag2page"
    query = DBSession.query_property()
    id = sa.Column(sa.Integer, primary_key=True)
    object_id = sa.Column(sa.Integer, sa.ForeignKey("page.id"))
    tag_id = sa.Column(sa.Integer, sa.ForeignKey("pagetag.id"))
    # page = orm.relationship("Page", backref=orm.backref("pagetag2page", cascade="all, delete-orphan"))


class PageTag(WithOrganizationMixin, Base):
    CLASSIFIER = "page"

    __tablename__ = "pagetag"
    query = DBSession.query_property()
    id = sa.Column(sa.Integer, primary_key=True)
    label = sa.Column(sa.Unicode(255), index=True)
    pages = orm.relationship("Page", secondary="pagetag2page", backref="tags")
    publicp = sa.Column(sa.Boolean, default=False)
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now)
    __table_args__ = ((saschema.UniqueConstraint(label, publicp), ))        

class AssetTag2Asset(Base):
    __tablename__ = "assettag2asset"
    query = DBSession.query_property()
    id = sa.Column(sa.Integer, primary_key=True)
    object_id = sa.Column(sa.Integer, sa.ForeignKey("asset.id"))
    tag_id = sa.Column(sa.Integer, sa.ForeignKey("assettag.id"))
    asset = orm.relationship("Asset", backref=orm.backref("assettag2asset", cascade="all, delete-orphan"))

class AssetTag(WithOrganizationMixin, Base):
    CLASSIFIER = "asset"

    __tablename__ = "assettag"
    id = sa.Column(sa.Integer, primary_key=True)
    query = DBSession.query_property()
    label = sa.Column(sa.Unicode(255), index=True)
    assets = orm.relationship("Asset", secondary="assettag2asset", backref="tags")
    publicp = sa.Column(sa.Boolean, default=False)
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now)

    discriminator = sa.Column("type", sa.String(32), nullable=False)
    __mapper_args__ = {"polymorphic_on": discriminator}
    __table_args__ = ((saschema.UniqueConstraint(label, discriminator, publicp), ))

## sigle table inheritance or concreate table inheritance?
class ImageAssetTag(AssetTag):
    type = "image"
    __mapper_args__ = {"polymorphic_identity": type}

class MovieAssetTag(AssetTag):
    type = "movie"
    __mapper_args__ = {"polymorphic_identity": type}

class FlashAssetTag(AssetTag):
    type = "flash"
    __mapper_args__ = {"polymorphic_identity": type}


class HotWord(WithOrganizationMixin, Base):
    query = DBSession.query_property()

    id = sa.Column(sa.Integer, primary_key=True)
    __tablename__ = "hotword"
    
    tag_id =  sa.Column(sa.Integer, sa.ForeignKey("pagetag.id"))
    tag = orm.relationship("PageTag", uselist=False, backref="hotwords")
    name = sa.Column(sa.Unicode(255))
    orderno = sa.Column(sa.Integer, default=100) # 0~100

    enablep = sa.Column(sa.Boolean, default=True)
    term_begin = sa.Column(sa.DateTime)
    term_end = sa.Column(sa.DateTime)

    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now)

    @classmethod
    def from_page(cls, page):
        qs = cls.query.filter(cls.tag_id==PageTag.id)
        qs = qs.filter(PageTag2Page.tag_id==PageTag.id).filter(PageTag2Page.object_id==Page.id)
        qs = qs.filter(Page.id==page.id)
        return qs
    
