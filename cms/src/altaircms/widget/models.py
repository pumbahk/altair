# coding: utf-8
"""
ウィジェット用のモデルを定義する。

設定が必要なウィジェットのみ情報を保持する。
"""

from datetime import datetime

from sqlalchemy.orm import relationship, mapper, column_property
from sqlalchemy.schema import Column, ForeignKey, Table, MetaData
from sqlalchemy import Integer, DateTime, Unicode, String
from sqlalchemy.sql.expression import join

from altaircms.models import Base, DBSession
from altaircms.asset.models import ImageAsset, MovieAsset, FlashAsset, CssAsset


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


mapper(Widget, widget, polymorphic_on=widget.c.type, polymorphic_identity='widget')
mapper(TextWidget, widget_text, inherits=Widget, polymorphic_identity='widget_text')
mapper(BreadcrumbsWidget, widget_breadcrumbs, inherits=Widget, polymorphic_identity='widget_breadcrumbs')



class Page2Widget(object):
    pass


"""
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
class Widget(Base):
    # ウィジェットの基底クラス
    __tablename__ = "widget"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())

    site_id = Column(Integer, ForeignKey("site.id"))

    def __repr__(self):
        return '<Widget %s>' % self.id

    def __unicode__(self):
        return '%s' % self.id


class TextWidget(Base):
    __tablename__ = "widget_text"

    id = Column(Integer, ForeignKey("widget.id"), primary_key=True)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())

    text = Column(Unicode)

"""

"""
class BreadcrumbsWidget(Base):
    #パンくずウィジェット
    #
    #現在のページ情報を元に階層構造を組み立てる？
    __tablename__ = "widget_breadcrumbs"

    id = Column(Integer, ForeignKey("widget.id"), primary_key=True)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())

    breadcrumb = Column(String)


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


class ImageWidget(Base):
    __tablename__ = 'widget_image'

    id = Column(Integer, ForeignKey("widget.id"), primary_key=True)
    asset_id = Column(Integer, ForeignKey(ImageAsset.id))


class MovieWidget(Base):
    __tablename__ = 'widget_movie'

    id = Column(Integer, ForeignKey("widget.id"), primary_key=True)
    asset_id = Column(Integer, ForeignKey(MovieAsset.id))


class FlashWidget(Base):
    __tablename__ = 'widget_flash'

    id = Column(Integer, ForeignKey("widget.id"), primary_key=True)
    asset_id = Column(Integer, ForeignKey(FlashAsset.id))


class BillingHistoryWidget(Base):
    __tablename__ = 'widget_billinghistory'

    id = Column(Integer, primary_key=True)
    widget_id = Column(Integer, ForeignKey("widget.id"))


class RakutenPointWidget(Base):
    __tablename__ = 'widget_rakutenpoint'

    id = Column(Integer, primary_key=True)
    widget_id = Column(Integer, ForeignKey("widget.id"))


"""
