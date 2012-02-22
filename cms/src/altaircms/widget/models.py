# coding: utf-8
"""
ウィジェット用のモデルを定義する。

設定が必要なウィジェットのみ情報を保持する。
"""

import sqlalchemy as sa
import sqlalchemy.orm as orm

from altaircms.models import Base, DBSession

from datetime import datetime
from zope.interface import implements
from altaircms.interfaces import IWidget
from altaircms.interfaces import IHasSite
from altaircms.interfaces import IHasTimeHistory


# from altaircms.plugins.widget.image.models import ImageWidget
# from altaircms.plugins.widget.freetext.models import FreetextWidget as TextWidget

__all__ = [
    # 'Widget',
     'ImageWidget',
    # 'MovieWidget',
    # 'FlashWidget',
    # 'MenuWidget',
     'TextWidget',
    # 'BreadcrumbsWidget',
    # 'TopicWidget',
]

WIDGET_TYPE = [
    'text',
    'breadcrumbs',
    'flash',
    'movie',
    'image',
    'topic',
    'menu',
    'billinghistory',
]

class Widget(Base):
    implements(IHasTimeHistory, IHasSite)

    query = DBSession.query_property()
    __tablename__ = "widget"
    page_id = sa.Column(sa.Integer, sa.ForeignKey("page.id"))
    id = sa.Column(sa.Integer, primary_key=True)
    site_id = sa.Column(sa.Integer, sa.ForeignKey("site.id"))
    discriminator = sa.Column("type", sa.String(32), nullable=False)
    created_at = sa.Column(sa.DateTime, default=datetime.now())
    updated_at = sa.Column(sa.DateTime, default=datetime.now())

    orm.relationship("Page", backref="widgets",
                     cascade="save-update, merge, delete, delete-orphan")
    __mapper_args__ = {"polymorphic_on": discriminator}

    def __init__(self, site_id, type_):
        self.site_id = site_id
        self.type = type_

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.id)

"""

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
    Column('asset_id', Integer, ForeignKey('asset.id'))
)

widget_image = Table(
    'widget_image',
    Base.metadata,
    Column('id', Integer, ForeignKey('widget.id'), primary_key=True),
    Column('asset_id', Integer, ForeignKey('asset.id'))
)

widget_topic = Table(
    'widget_topic',
    Base.metadata,
    Column('id', Integer, ForeignKey('widget.id'), primary_key=True),
    Column('topic_id', Integer, ForeignKey('topic.id')),
    Column('title', String)
)

widget_menu = Table(
    'widget_menu',
    Base.metadata,
    Column('id', Integer, ForeignKey('widget.id'), primary_key=True),
    Column('topic_id', Integer, ForeignKey('topic.id')),
    Column('menu', String)
)

class TextWidget(Widget):
    def __init__(self, captured):
        self.id = captured.get('id', None)
        self.site_id = captured.get('site_id', None)
        self.text = captured.get('text', None)

class MenuWidget(Widget):
    def __init__(self, captured):
        self.id = captured.get('id', None)
        self.site_id = captured.get('site_id', None)
        self.menu = captured.get('menu', None)

class BreadcrumbsWidget(Widget):
    def __init__(self, captured):
        self.id = captured.get('id', None)
        self.site_id = captured.get('site_id', None)
        self.breadcrumb = captured.get('breadcrumb', None)


class MovieWidget(Widget, AssetWidgetMixin):
    def __init__(self, captured):
        self.id = captured.get('id', None)
        self.site_id = captured.get('site_id', None)
        self.asset_id = captured.get('asset_id', None)


class FlashWidget(Widget, AssetWidgetMixin):
    def __init__(self, captured):
        self.id = captured.get('id', None)
        self.site_id = captured.get('site_id', None)
        self.asset_id = captured.get('asset_id', None)


class ImageWidget(Widget, AssetWidgetMixin):
    def __init__(self, captured):
        self.id = captured.get('id', None)
        self.site_id = captured.get('site_id', None)
        self.asset_id = captured.get('asset_id', None)


class TopicWidget(Widget):
    def __init__(self, captured):
        self.id = captured.get('id', None)
        self.site_id = captured.get('site_id', None)
        self.title = captured.get('title', None)
        self.topic_id = captured.get('topic_id', None)


mapper(Widget, widget, polymorphic_on=widget.c.type, polymorphic_identity='widget')
mapper(TextWidget, widget_text, inherits=Widget, polymorphic_identity='text')
mapper(BreadcrumbsWidget, widget_breadcrumbs, inherits=Widget, polymorphic_identity='breadcrumbs')
mapper(FlashWidget, widget_flash, inherits=Widget, polymorphic_identity='flash')
mapper(MovieWidget, widget_movie, inherits=Widget, polymorphic_identity='movie')
mapper(ImageWidget, widget_image, inherits=Widget, polymorphic_identity='image')
mapper(TopicWidget, widget_topic, inherits=Widget, polymorphic_identity='topic')
mapper(MenuWidget, widget_menu, inherits=Widget, polymorphic_identity='menu')


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
