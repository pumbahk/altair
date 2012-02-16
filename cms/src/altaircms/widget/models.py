# coding: utf-8
"""
ウィジェット用のモデルを定義する。

設定が必要なウィジェットのみ情報を保持する。
"""

from datetime import datetime

import sqlalchemy as sa
import sqlalchemy.orm as orm

from altaircms.models import Base, DBSession

__all__ = [
    'Widget',
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
    

class AssetWidgetMixin(object):
    _asset = None

    @property
    def asset(self):
        if not self.asset_id:
            return None

        if self._asset:
            return self._asset

        clsname = self.__class__.__name__[:self.__class__.__name__.rfind("Widget")] + 'Asset'
        cls = globals()[clsname]

        self._asset = DBSession.query(cls).get(self.asset_id)
        return self._asset


class Widget(Base):
    query = DBSession.query_property()
    __tablename__ = "widget"
    id = sa.Column(sa.Integer, primary_key=True)
    site_id = sa.Column(sa.Integer, sa.ForeignKey("site.id"))
    type = sa.Column(sa.String, nullable=False)

    def __init__(self, id_, site_id, type_):
        self.id = id_
        self.site_id = site_id
        self.type = type_

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.id)

    @property
    def appstruct(self):
        ## ウィジェットのプロパティを取得する
        attrs = [attr for attr in dir(self) if attr != 'appstruct' and not attr.startswith('_') and not callable(getattr(self, attr))]
        output = {}
        for attr in attrs:
            output[attr] = getattr(self, attr)

        return output

class FromDictMixin(object):
    @classmethod
    def from_dict(cls, D):
        instance = cls()
        for k, v in D.items():
            setattr(instance, k, v)
        return instance

class TextWidget(FromDictMixin, Base):
    type = "text"
    
    query = DBSession.query_property()
    __tablename__ = "widget_text"
    id = sa.Column(sa.Integer, primary_key=True)
    text = sa.Column(sa.Unicode)

    def __init__(self, id=None, text=None):
        self.id = id
        self.text = text

from altaircms.asset.models import *

class ImageWidget(FromDictMixin, Base):
    type = "image"

    query = DBSession.query_property()
    __tablename__ = "widget_image"
    id = sa.Column(sa.Integer, primary_key=True)
    asset_id = sa.Column(sa.Integer, sa.ForeignKey("asset.id"))
    asset = orm.relationship(ImageAsset, backref="widget", uselist=False)

    def __init__(self, id=None, asset_id=None):
        self.id = id
        self.asset_id = asset_id

class WidgetFetchException(Exception):
    pass

class WidgetFetcher(object):
    """ fetching a widget from a element of page.structure .
    e.g. {block_name: "image_widget",  pk: 1} => <ImageWidget object>
    """
    def fetch(self, name, pks):
        try:
            return getattr(self, name)(pks)
        except AttributeError:
            raise WidgetFetchException("%s model's fetch method is not defined" % name)

    def _query_by_object(self, model, pks):
        return DBSession.query(model).filter(model.id.in_(pks))

    def image_widget(self, pks):
        return self._query_by_object(ImageWidget, pks)

    def freetext_widget(self, pks):
        return self._query_by_object(TextWidget, pks)

## ?? ##
class Page2Widget(Base):
    __tablename__ = "page2widget"

    id = sa.Column(sa.Integer, primary_key=True)
    created_at = sa.Column(sa.DateTime, default=datetime.now())
    updated_at = sa.Column(sa.DateTime, default=datetime.now())

    block = sa.Column(sa.String) # HTMLのIDが入る想定
    order = sa.Column(sa.Integer) # ウィジェットの並び替え情報

    options = sa.Column(sa.String) # 何かしらの付加情報があればJSONシリアライズして保持する

    page_id = sa.Column(sa.Integer, sa.ForeignKey("page.id"))
    widget_id = sa.Column(sa.Integer, sa.ForeignKey("widget.id"))

    orm.relationship("Page", backref="widget")


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


