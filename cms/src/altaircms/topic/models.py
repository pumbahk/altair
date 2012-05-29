# -*- coding:utf-8 -*-

import sqlalchemy as sa
import sqlalchemy.orm as orm
from datetime import datetime

from altaircms.models import Base, BaseOriginalMixin
from altaircms.models import DBSession
from altaircms.page.models import PageSet
from altaircms.asset.models import ImageAsset
from altaircms.event.models import Event

import altaircms.helpers as h

"""
topicはtopicウィジェットで使われる。
以下のような内容の表示に使われる。

2011:2/11 講演者変更:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
2011:2/18 講演者変更:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
2011:2/19 講演者変更:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
2011:2/20 講演者中止:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx


要件として

1. 公開可否を指定できること
2. 最新N件を取得できること
3. (2.より優先して)表示順序を指定できること
    表示順序の範囲は　1 〜 100
    デフォルトでは50
4. 自動的に、ページ、イベントに紐ついたページ, 同カテゴリのものが表示される。

ができる必要がある。

"""

## 

class AboutPublishMixin(object):
    """ 表示順序を定義可能なmodelが持つ
    """
    publish_open_on = sa.Column(sa.DateTime)
    publish_close_on = sa.Column(sa.DateTime)
    orderno = sa.Column(sa.Integer, default=50)
    is_vetoed = sa.Column(sa.Boolean, default=False)
    
    @classmethod
    def publishing(cls, d=None, qs=None):
        if d is None:
            d = datetime.now()
        if qs is None:
            qs = cls.query
        return cls._has_permissions(cls._orderby_logic(cls._publishing(qs, d)))

    @classmethod
    def _has_permissions(cls, qs):
        """ 公開可能なもののみ
        """
        return qs.filter(cls.is_vetoed==False)

    @classmethod
    def _publishing(cls, qs, d):
        """ 掲載期間のもののみ
        """
        qs = qs.filter(cls.publish_open_on  <= d)
        return qs.filter(d <= cls.publish_close_on)

    @classmethod
    def _orderby_logic(cls, qs):
        """ 表示順序で並べた後、公開期間で降順
        """
        table = cls.__tablename__
        return qs.order_by(sa.asc(table+".orderno"),
                           sa.desc(table+".publish_open_on"), 
                           )



_where = object()

class Topic(AboutPublishMixin, 
            BaseOriginalMixin,
            Base):
    """
    トピック

各フィールドの説明
----------------------------------------

ページと結びついたフィールド
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

ページが結び付けられるフィールドは２つある。
(各フィールドの名前はpageで終わっているが、実際のところpagesetと結びついている)

+ linked_page: トピックがリンクとして利用される場合の飛び先
+ bound_page: トピックが表示されるページ

bound_pageに表示されたトピックをクリックするとlinked_pageに飛ぶということ。
※(kind=特集のトピックは、外部URLをtextに持つことができる。(plugins/widget/topic/sidebar_category_genre.mako, helers.link.get_link_from_topic))

各フィールドとtopic widgetでの表示条件について
--------------------------------------------------------------------------------

表示の絞りこみについては以下のフィールドが使われる

+ kind
+ subkind
+ event
+ bound_page
+ is_global

kindでトピックの種類を指定する。(e.g. トピックス, 特集, )

subkindでさらに細かく種類を分けることができる。しかし、通常のページではsubkindを使わない。
subkindを利用するのは、同じページ内で同じ種類のトピックを別の箇所に表示したい場合。
(subkindを利用するページとして、ヘルプページ、公演中止情報のページなどが挙げられる。)

event, bound_pageは任意。指定した際には、topic widgetでの絞り込みに用いることができる。

ちなみにtopic widgetでの検索条件の指定は以下３つが行える。

+ グローバルトピックを表示
+ ページに関連したトピックを表示
+ イベントに関連したトピックを表示

後者２つはand結合。それらとグローバルトピックはor結合。

グローバルトピックを表示の効果
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
グローバルトピックをONにしたとき、掲載期間内のis_global=Trueのトピックが常に表示されるようになる。

例えば、トップページ、音楽ページ(カテゴリトップ), 邦楽ページ(サブカテゴリトップ)などでトピックを共有したい時に使う。
(音楽ページ、邦楽ページのみで共有したい場合には、サブカテゴリと共に利用する)

各カテゴリページでのトピックの利用方法
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

各カテゴリページのみで表示するトピックを登録したい場合には、
以下のようなトピックを登録し、以下のようにtopic widgetを利用する。

Topic(kind=kind, page=category_page, is_global=False)で登録(kind は例えばトピックス)
topic widgetでは

+ グローバルトピックを表示 => OFF
+ ページに関連したトピックを表示 => ON
+ イベントに関連したトピックを表示 => OFF

イベントに関連したトピックを表示は各カテゴリページで利用しない。

イベントに関連したトピックを表示を利用するとき
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

イベントに関連したトピックを表示を利用するのは、イベント詳細ページに隣接するページでトピック表示を共有したい場合。
（隣接するページ=同一イベントを親に持つイベント詳細ページ以外のページ。
　詳細ページのタブメニューにリンクを持つページ。例えばイベントギャラリー、詳細説明（別ページ）など）

このとき、イベントに関連したトピックを表示のみをONにする。
    """

    query = DBSession.query_property()

    __tablename__ = "topic"
    KIND_CANDIDATES = [u"公演中止情報", u"トピックス", u"その他", u"ヘルプ", u"特集", u"特集(サブカテゴリ)"]

    id = sa.Column(sa.Integer, primary_key=True)
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now)

    client_id = sa.Column(sa.Integer, sa.ForeignKey("client.id")) #?
    site_id = sa.Column(sa.Integer, sa.ForeignKey("site.id"))   
    kind = sa.Column(sa.Unicode(255))
    subkind = sa.Column(sa.Unicode(255))
    title = sa.Column(sa.Unicode(255))
    text = sa.Column(sa.UnicodeText)
    event_id = sa.Column(sa.Integer, sa.ForeignKey("event.id"), nullable=True)
    event = orm.relationship(Event, backref="topic")
    
    ## topic をlinkとして利用したときの飛び先
    linked_page_id = sa.Column(sa.Integer, sa.ForeignKey("pagesets.id"), nullable=True)
    linked_page = orm.relationship(PageSet, primaryjoin="Topic.linked_page_id==PageSet.id")

    ## topicが表示されるページ
    bound_page_id = sa.Column(sa.Integer, sa.ForeignKey("pagesets.id"), nullable=True)
    bound_page = orm.relationship(PageSet, primaryjoin="Topic.bound_page_id==PageSet.id")
    is_global = sa.Column(sa.Boolean, default=False)

    def __repr__(self):
        return "topic: %s title=%s" % (self.kind, self.title)

    @property
    def topic_type(self):
        """ topicがどんな種類で関連付けられているか調べる
        pageよりeventが優先 => eventが存在＝event詳細ページのどれか
        """
        if self.is_global:
            return "global"
        elif self.event:
            return "event:%d" % self.event.id
        elif self.bound_page:
            return "page:%d" % self.bound_page.id
        else:
            return None

    @classmethod
    def matched_topic_type(cls, page=None, event=None, qs=None):
        if qs is None:
            qs = cls.query

        where = _where
        if page:
            where = (Topic.bound_page==page) if where  == _where else where & (Topic.bound_page==page)
        if event:
            where = (Topic.event==event) if where   == _where else where & (Topic.event==event)

        if where  == _where: 
            return qs.filter(cls.is_global==True)
        else:
            return qs.filter(where | (cls.is_global==True))

    @classmethod
    def matched_qs(cls, d=None, page=None, event=None, qs=None, kind=None, subkind=None):
        """ 下にある内容の通りのtopicsを返す
        """
        qs = cls.publishing(d=d, qs=qs)
        qs = cls.matched_topic_type(qs=qs, page=page, event=event)

        if kind:
            qs = qs.filter_by(kind=kind)
        if subkind:
            qs = qs.filter_by(subkind=subkind)
        return qs

class Topcontent(AboutPublishMixin,
                 BaseOriginalMixin,
                 Base):
    """
    Topページの画像つきtopicのようなもの
    """
    __tablename__ = "topcontent"
    query = DBSession.query_property()
    COUNTDOWN_CANDIDATES = h.base.COUNTDOWN_KIND_MAPPING.items()
    KIND_CANDIDATES = [u"注目のイベント"]

    id = sa.Column(sa.Integer, primary_key=True)
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now)

    client_id = sa.Column(sa.Integer, sa.ForeignKey("client.id")) #?
    site_id = sa.Column(sa.Integer, sa.ForeignKey("site.id"))   
    kind = sa.Column(sa.Unicode(255))
    subkind = sa.Column(sa.Unicode(255))
    title = sa.Column(sa.Unicode(255))
    text = sa.Column(sa.Unicode(255))

    ## topcontent をlinkとして利用したときの飛び先
    linked_page_id = sa.Column(sa.Integer, sa.ForeignKey("pagesets.id"), nullable=True)
    linked_page = orm.relationship(PageSet, primaryjoin="Topcontent.linked_page_id==PageSet.id")

    ## topcontentが表示されるページ
    bound_page_id = sa.Column(sa.Integer, sa.ForeignKey("pagesets.id"), nullable=True)
    bound_page = orm.relationship(PageSet, primaryjoin="Topcontent.bound_page_id==PageSet.id")

    ## extend
    image_asset_id = sa.Column(sa.Integer, sa.ForeignKey("image_asset.id"), nullable=True)
    image_asset = orm.relationship(ImageAsset, backref="topcontent")
    countdown_type = sa.Column(sa.String(255)) #todo: fixme
    is_global = sa.Column(sa.Boolean, default=True)

    def __repr__(self):
        return "topcontent: %s title=%s" % (self.kind, self.title)

    @property
    def countdown_type_ja(self):
        return h.base.countdown_kind_ja(self.countdown_type)

    @property
    def countdown_limit(self):
        return getattr(self.linked_page.event, self.countdown_type)

    @classmethod
    def matched_qs(cls, d=None, page=None, qs=None, kind=None, subkind=None):
        """ 下にある内容の通りのtopcontentsを返す
        """
        qs = cls.publishing(d=d, qs=qs)
        qs = cls.matched_topcontent_type(qs=qs, page=page)
        if kind:
            qs = qs.filter_by(kind=kind)
        if subkind:
            qs =  qs.filter_by(subkind=subkind)
        return qs

    @property
    def topcontent_type(self):
        """ topcontentがどんな種類で関連付けられているか調べる
        pageよりeventが優先 => eventが存在＝event詳細ページのどれか
        """
        if self.is_global:
            return "global"
        elif self.bound_page:
            return "page:%d" % self.bound_page_id
        else:
            return None

    @classmethod
    def matched_topcontent_type(cls, page=None, event=None, qs=None):
        if qs is None:
            qs = cls.query

        where = _where
        if page:
            where = (Topcontent.bound_page==page) if where  == _where else where & (Topcontent.bound_page==page)
        if event:
            where = (Topcontent.event==event) if where   == _where else where & (Topcontent.event==event)

        if where  == _where: 
            return qs.filter(cls.is_global==True)
        else:
            return qs.filter(where | (cls.is_global==True))

