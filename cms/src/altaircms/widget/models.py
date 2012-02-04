# coding: utf-8
"""
ウィジェット用のモデルを定義する。

設定が必要なウィジェットのみ情報を保持する。
"""

from datetime import datetime
from pyramid.renderers import render

from sqlalchemy.orm import relationship, mapper
from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy import Integer, DateTime, Unicode, String

from altaircms.models import Base
from altaircms.asset.models import ImageAsset, MovieAsset, FlashAsset, CssAsset

__all__ = [
#    'Widget',
    'ImageWidget',
    'MovieWidget',
    'FlashWidget',
    'TextWidget',
    'BreadcrumbsWidget',
]


widget = Table(
    'widget',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('site_id', Integer, ForeignKey("site.id")),
    Column('type', String, nullable=False)
)

widget_text = Table(
    'widget_text',
    Base.metadata,
    Column('id', Integer, ForeignKey('widget.id'), primary_key=True),
    Column('text', Unicode)
)

widget_breadcrumbs = Table(
    'widget_breadcrumbs',
    Base.metadata,
    Column('id', Integer, ForeignKey('widget.id'), primary_key=True),
    Column('breadcrumb', String)
)

widget_flash = Table(
    'widget_flash',
    Base.metadata,
    Column('id', Integer, ForeignKey('widget.id'), primary_key=True),
    Column('asset_id', Integer, ForeignKey('asset.id'))
)

widget_movie = Table(
    'widget_movie',
    Base.metadata,
    Column('id', Integer, ForeignKey('widget.id'), primary_key=True),
    Column('asset_id', Integer, ForeignKey('asset.id')),
)

widget_image = Table(
    'widget_image',
    Base.metadata,
    Column('id', Integer, ForeignKey('widget.id'), primary_key=True),
    Column('asset_id', Integer, ForeignKey('asset.id'))
)


class Widget(object):
    def __init__(self, id_, site_id, type_):
        self.id = id_
        self.site_id = site_id
        self.type = type_


class TextWidget(Widget):
    def __init__(self, id_, site_id, text):
        self.id = id_
        self.site_id = site_id
        self.text = text


class BreadcrumbsWidget(Widget):
    def __init__(self, id_, site_id, breadcrumb):
        self.id = id_
        self.site_id = site_id
        self.breadcrumb = breadcrumb


class FlashWidget(Widget):
    def __init__(self, id_, site_id, url, title, mimetype):
        self.id = id_
        self.site_id = site_id
        self.type = type_
        self.url = url
        self.title = title
        self.mimetype = mimetype


class MovieWidget(Widget):
    def __init__(self, id_, site_id, url, title, mimetype):
        self.id = id_
        self.site_id = site_id
        self.breadcrumb = breadcrumb
        self.url = url
        self.title = title
        self.mimetype = mimetype


class ImageWidget(Widget):
    def __init__(self, id_, site_id, url, title):
        self.id = id_
        self.site_id = site_id
        self.breadcrumb = breadcrumb
        self.url = url
        self.title = title
        self.mimetype = mimetype


mapper(Widget, widget, polymorphic_on=widget.c.type, polymorphic_identity='widget')
mapper(TextWidget, widget_text, inherits=Widget, polymorphic_identity='widget_text')
mapper(BreadcrumbsWidget, widget_breadcrumbs, inherits=Widget, polymorphic_identity='widget_breadcrumbs')
mapper(FlashWidget, widget_flash, inherits=Widget, polymorphic_identity='widget_flash')
mapper(MovieWidget, widget_movie, inherits=Widget, polymorphic_identity='widget_movie')
mapper(ImageWidget, widget_image, inherits=Widget, polymorphic_identity='widget_image')



class Page2Widget(Base):
    __tablename__ = "page2widget"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())

    block = Column(String) # HTMLのIDが入る想定
    order = Column(Integer) # ウィジェットの並び替え情報

    options = Column(String) # 何かしらの付加情報があればJSONシリアライズして保持する

    page_id = Column(Integer, ForeignKey("page.id"))
    widget_id = Column(Integer, ForeignKey("widget.id"))

    relationship("Page", backref="widget")


"""
class Asset2Widget(Base):
    __tablename__ = "asset2widget"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())

    position = Column(String) # 何かしらのレイアウト情報をシリアライズして保持する想定

    asset_id = Column(Integer, ForeignKey("asset.id"))
    widget_d = Column(Integer, ForeignKey("widget.id"))
"""

"""
class MenuWidget(Base):
    __tablename__ = "widget_menu"

    id = Column(Integer, ForeignKey("widget.id"), primary_key=True)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())

    menu = Column(String)


class TwitterTimelineWidget(Base):
    __tablename__ = "widget_twitter_timeline"

    id = Column(Integer, ForeignKey("widget.id"), primary_key=True)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())

    screen_name = Column(String)

class TwitterSearchWidget(Base):
    __tablename__ = "widget_twitter_search"

    id = Column(Integer, ForeignKey("widget.id"), primary_key=True)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())

    search_word = Column(Unicode)


class TopicWidget(Base):
    __tablename__ = "widget_topic"

    id = Column(Integer, ForeignKey("widget.id"), primary_key=True)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())

    topic_type = Column(Integer)
    view_limit = Column(Integer)

class FacebookWidget(Base):
    __tablename__ = 'widget_facebook'

    id = Column(Integer, ForeignKey("widget.id"), primary_key=True)
    url = Column(String)


class BillingHistoryWidget(Base):
    __tablename__ = 'widget_billinghistory'

    id = Column(Integer, primary_key=True)
    widget_id = Column(Integer, ForeignKey("widget.id"))


class RakutenPointWidget(Base):
    __tablename__ = 'widget_rakutenpoint'

    id = Column(Integer, primary_key=True)
    widget_id = Column(Integer, ForeignKey("widget.id"))


"""
