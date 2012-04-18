# coding: utf-8


import sqlalchemy as sa
import sqlalchemy.orm as orm
from altaircms.models import Base, BaseOriginalMixin
from altaircms.models import DBSession

from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property
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

import os
DIR = os.path.dirname(os.path.abspath(__file__))
# import sqlalchemy.orm as orm

class Asset(BaseOriginalMixin, Base):
    implements(IHasTimeHistory, IHasSite)
    query = DBSession.query_property()
    __tablename__ = "asset"

    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.Unicode(255))
    discriminator = sa.Column("type", sa.String(32), nullable=False)

    created_at = sa.Column(sa.DateTime, default=datetime.now())
    updated_at = sa.Column(sa.DateTime, default=datetime.now())

    created_by_id = sa.Column(sa.Integer, sa.ForeignKey("operator.id"))
    created_by = orm.relationship("Operator", backref="created_assets",
                                  primaryjoin="Asset.created_by_id==Operator.id")
    updated_by_id = sa.Column(sa.Integer, sa.ForeignKey("operator.id"))
    updated_by = orm.relationship("Operator", backref="updated_assets", 
                                  primaryjoin="Asset.updated_by_id==Operator.id")

    site_id =  sa.Column(sa.Integer, sa.ForeignKey("site.id"))

    __mapper_args__ = {"polymorphic_on": discriminator}

    def __repr__(self):
        return '<%s %s %s>' % (self.__class__.__name__, self.id, self.filepath)

    ## todo refactoring?
    @hybrid_property
    def public_tags(self):
        return [tag for tag in self.tags if tag.publicp == True]

    @hybrid_property
    def private_tags(self):
        return [tag for tag in self.tags if tag.publicp == False]

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
    mimetype = sa.Column(sa.String(255), default="")

class FlashAsset(Asset):
    DEFAULT_IMAGE_PATH = os.path.join(DIR, "img/not_found.jpg")
    
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
    imagepath = sa.Column(sa.String(255), default=DEFAULT_IMAGE_PATH)

class MovieAsset(Asset):
    DEFAULT_IMAGE_PATH = os.path.join(DIR, "img/not_found.jpg")

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
    imagepath = sa.Column(sa.String(255), default=DEFAULT_IMAGE_PATH)

# class CssAsset(Asset):
#     pass
