
import sqlalchemy as sa
import sqlalchemy.orm as orm
import sqlalchemy.schema as saschema
from altaircms.models import Base
from altaircms.models import DBSession

from datetime import datetime
from altaircms.page.models import Page
from altaircms.asset.models import Asset
from altaircms.asset.models import ImageAsset
from altaircms.asset.models import MovieAsset
from altaircms.asset.models import FlashAsset
from altaircms.models import WithOrganizationMixin

class PageTag2Page(Base):
    __tablename__ = "pagetag2page"
    query = DBSession.query_property()
    id = sa.Column(sa.Integer, primary_key=True)
    object_id = sa.Column(sa.Integer, sa.ForeignKey("page.id"))
    tag_id = sa.Column(sa.Integer, sa.ForeignKey("pagetag.id"))


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

def delete_orphan_pagetag(mapper, connection, target):
    PageTag.query.filter(~PageTag.pages.any()).delete(synchronize_session=False)
sa.event.listen(Page, "after_delete", delete_orphan_pagetag)

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

def delete_orphan_assettag(mapper, connection, target):
    AssetTag.query.filter(~AssetTag.assets.any()).delete(synchronize_session=False)
sa.event.listen(Asset, "after_delete", delete_orphan_assettag)


## sigle table inheritance or concreate table inheritance?
class ImageAssetTag(AssetTag):
    type = "image"
    __mapper_args__ = {"polymorphic_identity": type}
def delete_orphan_imageassettag(mapper, connection, target):
    ImageAssetTag.query.filter(~ImageAssetTag.assets.any()).delete(synchronize_session=False)
sa.event.listen(ImageAsset, "after_delete", delete_orphan_imageassettag)

class MovieAssetTag(AssetTag):
    type = "movie"
    __mapper_args__ = {"polymorphic_identity": type}
def delete_orphan_movieassettag(mapper, connection, target):
    MovieAssetTag.query.filter(~MovieAssetTag.assets.any()).delete(synchronize_session=False)
sa.event.listen(MovieAsset, "after_delete", delete_orphan_movieassettag)

class FlashAssetTag(AssetTag):
    type = "flash"
    __mapper_args__ = {"polymorphic_identity": type}
def delete_orphan_flashassettag(mapper, connection, target):
    FlashAssetTag.query.filter(~FlashAssetTag.assets.any()).delete(synchronize_session=False)
sa.event.listen(FlashAsset, "after_delete", delete_orphan_flashassettag)


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
    
