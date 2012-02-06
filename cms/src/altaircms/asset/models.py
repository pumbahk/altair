# coding: utf-8
from datetime import datetime

from sqlalchemy.orm import mapper
from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy import Integer, DateTime, String
from zope.sqlalchemy.tests import metadata

from altaircms.models import Base, Site

__all__ = [
    'Asset',
    'ImageAsset',
    'MovieAsset',
    'FlashAsset',
    'CssAsset'
]


class Asset(object):
    pass

class ImageAsset(Asset):
    def __init__(self, filepath, alt='', size=None, width=None, height=None, mimetype=None):
        self.alt = alt
        self.size = size
        self.width = width
        self.height = height
        self.filepath = filepath
        self.mimetype = mimetype

class MovieAsset(Asset):
    pass

class FlashAsset(Asset):
    pass

class CssAsset(Asset):
    pass


asset_table = Table(
    "asset",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("site_id", Integer, ForeignKey(Site.__table__.c.id)),
    Column("filepath", String),
    Column("size", Integer),
    Column('width', Integer),
    Column('height', Integer),
    Column('length', Integer),
    Column('mimetype', String),
    Column('type', String(30))
)

asset_mapper = mapper(Asset, asset_table, polymorphic_on=asset_table.c.type, polymorphic_identity='asset')
image_asset_mapper = mapper(ImageAsset, inherits=asset_mapper, polymorphic_identity='image_asset')
mapper(MovieAsset, inherits=asset_mapper, polymorphic_identity='movie_asset')
mapper(FlashAsset, inherits=asset_mapper, polymorphic_identity='flash_asset')
mapper(CssAsset, inherits=asset_mapper, polymorphic_identity='css_asset')
