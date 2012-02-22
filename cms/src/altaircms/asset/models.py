# coding: utf-8
from altaircms.models import Base
from altaircms.models import DBSession

__all__ = [
    'Asset',
    'ImageAsset',
    'MovieAsset',
    'FlashAsset',
    # 'CssAsset'
]

import sqlalchemy as sa
# import sqlalchemy.orm as orm
from sqlalchemy.ext.declarative import declared_attr

class Asset(Base):
    query = DBSession.query_property()
    __tablename__ = "asset"

    id = sa.Column(sa.Integer, primary_key=True)
    discriminator = sa.Column("type", sa.String(32), nullable=False)
    __mapper_args__ = {"polymorphic_on": discriminator}

    def __repr__(self):
        return '<%s %s %s>' % (self.__class__.__name__, self.id, self.filepath)

class MediaAssetColumnsMixin(object):
    @declared_attr
    def site_id(cls):
    ## Columns with foreign keys to other columns must be declared as @declared_attr callables on declarative mixin classes
        return sa.Column(sa.Integer, sa.ForeignKey("site.id"))

    alt = sa.Column(sa.Integer)
    size = sa.Column(sa.Integer)
    width = sa.Column(sa.Integer)
    height = sa.Column(sa.Integer)
    filepath = sa.Column(sa.String)
    mimetype = sa.Column(sa.String, default="")

    ## has default constractor. so this class is called at `Treat' rather than `mixin'.
    def __init__(self, filepath='', alt='', size=None, width=None, height=None, mimetype=None):
        self.alt = alt
        self.size = size
        self.width = width
        self.height = height
        self.filepath = filepath
        self.mimetype = mimetype or self.MIMETYPE_DEFAULT
    MIMETYPE_DEFAULT = ''

class ImageAsset(MediaAssetColumnsMixin, Asset):
    __tablename__ = "image_asset"
    __mapper_args__ = {"polymorphic_identity": "image"}
    id = sa.Column(sa.Integer, sa.ForeignKey("asset.id"), primary_key=True)


class FlashAsset(MediaAssetColumnsMixin, Asset):
    MIMETYPE_DEFAULT = 'application/x-shockwave-flash'

    __tablename__ = "flash_asset"
    __mapper_args__ = {"polymorphic_identity": "flash"}
    id = sa.Column(sa.Integer, sa.ForeignKey("asset.id"), primary_key=True)
    mimetype = sa.Column(sa.String, default='application/x-shockwave-flash')

class MovieAsset(MediaAssetColumnsMixin, Asset):
    __tablename__ = "movie_asset"
    __mapper_args__ = {"polymorphic_identity": "movie"}
    id = sa.Column(sa.Integer, sa.ForeignKey("asset.id"), primary_key=True)

# class CssAsset(Asset):
#     pass
