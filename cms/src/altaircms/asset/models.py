# coding: utf-8
from datetime import datetime

from pyramid.url import route_url

from sqlalchemy.orm import mapper, relationship
from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy import Integer, DateTime, String
from zope.sqlalchemy.tests import metadata
from sqlalchemy.sql.expression import and_

from altaircms.models import Base
from altaircms.models import Site
from altaircms.models import DBSession

__all__ = [
    'Asset',
    'ImageAsset',
    'MovieAsset',
    'FlashAsset',
    'CssAsset'
]


class Asset(object):
    query = DBSession.query_property()
    def __repr__(self):
        return '<%s %s %s>' % (self.__class__.__name__, self.id, self.filepath)

    def get_url(self):
        return route_url('asset_view', asset_id=self.id)
    __ks__ = ["id", "site_id", "filepath", "size", "width", "height", "length", "mimetype", "type"]

    def to_dict(self):
        return {k: getattr(self, k) for k in self.__ks__ if hasattr(self, k)}

    @classmethod
    def from_dict(cls, D):
        instance = cls(None)
        for k in cls.__ks__:
            setattr(instance, k, D.get(k))
        return instance


class ImageAsset(Asset):
    query = DBSession.query_property()
    def __init__(self, filepath, alt='', size=None, width=None, height=None, mimetype=None):
        self.alt = alt
        self.size = size
        self.width = width
        self.height = height
        self.filepath = filepath
        self.mimetype = mimetype


class MovieAsset(Asset):
    def __init__(self, filepath, length=None, width=None, height=None, mimetype=None):
        self.length = length
        self.width = width
        self.height = height
        self.filepath = filepath
        self.mimetype = mimetype


class FlashAsset(Asset):
    def __init__(self, filepath, size=None, width=None, height=None):
        self.size = size
        self.width = width
        self.height = height
        self.filepath = filepath
        self.mimetype = 'application/x-shockwave-flash'


class CssAsset(Asset):
    pass


##
## 単一テーブル継承を使用しているが、ウィジェットなどと同様に結合テーブル継承に切り替えたほうがいいかも知れない
##
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
