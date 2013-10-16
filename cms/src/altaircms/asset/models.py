# coding: utf-8


import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.ext.declarative import declared_attr
from altaircms.models import Base, BaseOriginalMixin
from altaircms.models import DBSession

from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property
from zope.interface import implements
from altaircms.interfaces import IAsset
from altaircms.interfaces import IHasMedia
from altaircms.models import WithOrganizationMixin
import os
import itertools

__all__ = [
    'Asset',
    'ImageAsset',
    'MovieAsset',
    'FlashAsset',
    # 'CssAsset'
]
DIR = os.path.dirname(os.path.abspath(__file__))
# import sqlalchemy.orm as orm

class Asset(BaseOriginalMixin, WithOrganizationMixin, Base):
    query = DBSession.query_property()
    __tablename__ = "asset"

    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.Unicode(255))
    discriminator = sa.Column("type", sa.String(32), nullable=False)

    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.now)

    created_by_id = sa.Column(sa.Integer, sa.ForeignKey("operator.id"))
    created_by = orm.relationship("Operator", backref="created_assets",
                                  primaryjoin="Asset.created_by_id==Operator.id")
    updated_by_id = sa.Column(sa.Integer, sa.ForeignKey("operator.id"))
    updated_by = orm.relationship("Operator", backref="updated_assets", 
                                  primaryjoin="Asset.updated_by_id==Operator.id")

    __mapper_args__ = {"polymorphic_on": discriminator}

    def __repr__(self):
        return '<%s %s %s>' % (self.__class__.__name__, self.id, self.filepath)

    ## todo refactoring?
    @property
    def public_tags(self):
        return [tag for tag in self.tags if tag.publicp == True]

    @property
    def private_tags(self):
        return [tag for tag in self.tags if tag.publicp == False]

    def increment_version(self):
        if self.version_counter is None:
            self.version_counter = 0
        self.version_counter += 1
        return self.version_counter

    def all_files_candidates(self):
        """ version conter -> [filepath] + [thumbnail_path]
        """
        c = self.version_counter
        filepath = self.filepath
        for i in range((c or 0) + 1):
            yield filename_with_version(filepath, i)

        thumbnail_path = self.thumbnail_path
        if thumbnail_path:
            for i in range((c or 0) + 1):
                yield filename_with_version(thumbnail_path, i)

    def filename_with_version(self, path=None, version=None):
        path = path or self.filepath
        return filename_with_version(path, version or self.version_counter)

def filename_with_version(fname, i):
    if i == 0:
        return fname
    base, ext = os.path.splitext(fname)
    return "{0}.{1}{2}".format(base, i, ext)

class ImageAsset(Asset):
    implements(IAsset, IHasMedia)
    type = "image"

    __tablename__ = "image_asset"
    __mapper_args__ = {"polymorphic_identity": type}

    id = sa.Column(sa.Integer, sa.ForeignKey("asset.id"), primary_key=True)
    alt = sa.Column(sa.Integer)
    size = sa.Column(sa.Integer)
    width = sa.Column(sa.Integer)
    height = sa.Column(sa.Integer)
    filepath = sa.Column(sa.String(255))
    thumbnail_path = sa.Column(sa.String(255))
    file_url = sa.Column(sa.String(255))
    thumbnail_url = sa.Column(sa.String(255))
    mimetype = sa.Column(sa.String(255), default="")
    version_counter = sa.Column(sa.SmallInteger, default=0, nullable=False)

    @property
    def image_path(self):
        return self.filepath

    @property
    def image_url(self):
        return self.file_url


class FlashAsset(Asset):
    implements(IAsset, IHasMedia)
    type = "flash"
    MIMETYPE_DEFAULT = 'application/x-shockwave-flash'

    __tablename__ = "flash_asset"
    __mapper_args__ = {"polymorphic_identity": type}

    id = sa.Column(sa.Integer, sa.ForeignKey("asset.id"), primary_key=True)
    alt = sa.Column(sa.Integer)
    size = sa.Column(sa.Integer)
    width = sa.Column(sa.Integer)
    height = sa.Column(sa.Integer)
    filepath = sa.Column(sa.String(255))
    mimetype = sa.Column(sa.String(255), default='application/x-shockwave-flash')
    thumbnail_path = sa.Column(sa.String(255))
    file_url = sa.Column(sa.String(255))
    thumbnail_url = sa.Column(sa.String(255))
    version_counter = sa.Column(sa.SmallInteger, default=0, nullable=False)

    @property
    def image_path(self):
        return self.thumbnail_path

    @property
    def image_url(self):
        return self.thumbnail_url

class MovieAsset(Asset):
    implements(IAsset, IHasMedia)
    type = "movie"

    __tablename__ = "movie_asset"
    __mapper_args__ = {"polymorphic_identity": type}

    id = sa.Column(sa.Integer, sa.ForeignKey("asset.id"), primary_key=True)
    alt = sa.Column(sa.Integer)
    size = sa.Column(sa.Integer)
    width = sa.Column(sa.Integer)
    height = sa.Column(sa.Integer)
    filepath = sa.Column(sa.String(255))
    mimetype = sa.Column(sa.String(255), default="")
    thumbnail_path = sa.Column(sa.String(255))
    file_url = sa.Column(sa.String(255))
    thumbnail_url = sa.Column(sa.String(255))
    version_counter = sa.Column(sa.SmallInteger, default=0, nullable=False)

    @property
    def image_path(self):
        return self.thumbnail_path

    @property
    def image_url(self):
        return self.thumbnail_url

# class CssAsset(Asset):
#     pass

class AssetTag2Asset(Base):
    __tablename__ = "assettag2asset"
    query = DBSession.query_property()
    object_id = sa.Column(sa.Integer, sa.ForeignKey("asset.id"), primary_key=True)
    tag_id = sa.Column(sa.Integer, sa.ForeignKey("assettag.id"), primary_key=True)
    asset = orm.relationship("Asset", backref=orm.backref("assettag2asset", cascade="all, delete-orphan"))
    __tableargs__ = (
        sa.UniqueConstraint("object_id", "tag_id") 
        )

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

    def __repr__(self):
        return "<%r label: %r organization_id: %r>" % (self.__class__, self.label, self.organization_id)

def delete_orphan_assettag(mapper, connection, target):
    AssetTag.query.filter(~AssetTag.assets.any()).delete(synchronize_session=False)
sa.event.listen(Asset, "after_delete", delete_orphan_assettag)


## sigle table inheritance or concreate table inheritance?
class ImageAssetTag(AssetTag):
    type = "image"
    __mapper_args__ = {"polymorphic_identity": type}
    @declared_attr
    def __tableargs__(cls):
        return  ((sa.schema.UniqueConstraint(cls.label, cls.discriminator, cls.organization_id)))        


def delete_orphan_imageassettag(mapper, connection, target):
    ImageAssetTag.query.filter(~ImageAssetTag.assets.any()).delete(synchronize_session=False)
sa.event.listen(ImageAsset, "after_delete", delete_orphan_imageassettag)

class MovieAssetTag(AssetTag):
    type = "movie"
    __mapper_args__ = {"polymorphic_identity": type}
    @declared_attr
    def __tableargs__(cls):
        return  ((sa.schema.UniqueConstraint(cls.label, cls.discriminator, cls.organization_id)))        

def delete_orphan_movieassettag(mapper, connection, target):
    MovieAssetTag.query.filter(~MovieAssetTag.assets.any()).delete(synchronize_session=False)
sa.event.listen(MovieAsset, "after_delete", delete_orphan_movieassettag)

class FlashAssetTag(AssetTag):
    type = "flash"
    __mapper_args__ = {"polymorphic_identity": type}
    @declared_attr
    def __tableargs__(cls):
        return  ((sa.schema.UniqueConstraint(cls.label, cls.discriminator, cls.organization_id)))        

def delete_orphan_flashassettag(mapper, connection, target):
    FlashAssetTag.query.filter(~FlashAssetTag.assets.any()).delete(synchronize_session=False)
sa.event.listen(FlashAsset, "after_delete", delete_orphan_flashassettag)
