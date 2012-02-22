# coding: utf-8
from datetime import datetime

from sqlalchemy.orm import mapper
from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy.types import Integer, Unicode, DateTime, String
from altaircms.models import Base


__all__ = [ 'EventTag', 'PageTag', 'AssetTag']


class Tag(object):
    pass

class PageTag(Tag):
    pass

class EventTag(Tag):
    pass

class AssetTag(Tag):
    pass


tags = Table(
    "tag",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("name", Unicode),
    Column("is_public", Integer, default=0),
    Column("site_id", Integer, ForeignKey("site.id")),
    Column("type", String),
    Column("created_at", DateTime, default=datetime.now()),
    Column("updated_at", DateTime, default=datetime.now())
)

page_tags = Table(
    "tag_page",
    Base.metadata,
    Column("tag_id", Integer, ForeignKey('tag.id'), primary_key=True),
    Column("page_id", Integer, ForeignKey('page.id'))
)

event_tags = Table(
    "tag_event",
    Base.metadata,
    Column("tag_id", Integer, ForeignKey('tag.id'), primary_key=True),
    Column("event_id", Integer, ForeignKey("event.id"))
)

asset_tags = Table(
    "tag_asset",
    Base.metadata,
    Column("tag_id", Integer, ForeignKey('tag.id'), primary_key=True),
    Column("asset_id", Integer, ForeignKey('asset.id'))
)


mapper(Tag, tags, polymorphic_on=tags.c.type, polymorphic_identity='tag')
mapper(PageTag, page_tags, inherits=Tag, polymorphic_identity='page_tag')
mapper(EventTag, event_tags, inherits=Tag, polymorphic_identity='event_tag')
mapper(AssetTag, asset_tags, inherits=Tag, polymorphic_identity='asset_tag')

