# coding: utf-8


from altaircms.models import Base
from altaircms.models import DBSession

from datetime import datetime
from zope.interface import implements
from altaircms.interfaces import IAsset
from altaircms.interfaces import IHasMedia
from altaircms.interfaces import IHasSite
from altaircms.interfaces import IHasTimeHistory

__all__ = [
    'Asset',
    'ImageAsset',
    'MovieAsset',
    'FlashAsset',
    # 'CssAsset'
]

import sqlalchemy as sa
# import sqlalchemy.orm as orm

class Asset(Base):
    implements(IHasTimeHistory, IHasSite)
    query = DBSession.query_property()
    __tablename__ = "asset"

    id = sa.Column(sa.Integer, primary_key=True)
    discriminator = sa.Column("type", sa.String(32), nullable=False)
    created_at = sa.Column(sa.DateTime, default=datetime.now())
    updated_at = sa.Column(sa.DateTime, default=datetime.now())
    site_id =  sa.Column(sa.Integer, sa.ForeignKey("site.id"))

    __mapper_args__ = {"polymorphic_on": discriminator}

    def __repr__(self):
        return '<%s %s %s>' % (self.__class__.__name__, self.id, self.filepath)

class MediaAssetColumnsMixin(object):
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
    implements(IAsset, IHasMedia)
    type = "image"

    __tablename__ = "image_asset"
    __mapper_args__ = {"polymorphic_identity": type}

    id = sa.Column(sa.Integer, sa.ForeignKey("asset.id"), primary_key=True)

class FlashAsset(MediaAssetColumnsMixin, Asset):
    implements(IAsset, IHasMedia)
    type = "flash"
    MIMETYPE_DEFAULT = 'application/x-shockwave-flash'

    __tablename__ = "flash_asset"
    __mapper_args__ = {"polymorphic_identity": type}

    id = sa.Column(sa.Integer, sa.ForeignKey("asset.id"), primary_key=True)
    mimetype = sa.Column(sa.String, default='application/x-shockwave-flash')

class MovieAsset(MediaAssetColumnsMixin, Asset):
    implements(IAsset, IHasMedia)
    type = "movie"

    __tablename__ = "movie_asset"
    __mapper_args__ = {"polymorphic_identity": type}

    id = sa.Column(sa.Integer, sa.ForeignKey("asset.id"), primary_key=True)

# class CssAsset(Asset):
#     pass
