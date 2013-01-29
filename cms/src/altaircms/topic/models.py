# -*- coding:utf-8 -*-
import re
import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.ext.declarative import declared_attr
from datetime import datetime

from altaircms.models import Base, BaseOriginalMixin
from altaircms.models import DBSession, model_to_dict
from altaircms.page.models import PageSet
from altaircms.asset.models import ImageAsset
from altaircms.models import WithOrganizationMixin
import altaircms.helpers as h

"""
topicはtopicウィジェットで使われる。
以下のような内容の表示に使われる。

2011:2/11 公演者変更:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
2011:2/18 公演者変更:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
2011:2/19 公演者変更:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
2011:2/20 公演者中止:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx


要件として

1. 公開可否を指定できること
2. 最新N件を取得できること
3. (2.の日時に基づく順序より優先して)表示順序を指定できること
    表示順序の範囲は　1 〜 100 
    デフォルトでは50


※種々の理由により以下のようなモデルと日本語名の対応
* Topic -> トピック(テキスト)
* Topcontent -> トピック(画像)
* Promotion -> プロモーション枠(カルーセル)

"""

## 

def qs_has_permission(cls, qs):
    """ 公開可能なもののみ
    """
    return qs.filter(cls.is_vetoed==False)


def qs_in_term(cls,qs, d):
    """ 掲載期間のもののみ
    """
    qs = qs.filter(cls.publish_open_on  <= d)
    return qs.filter((d <= cls.publish_close_on) | (cls.publish_close_on == None))


def qs_orderby_logic(cls, qs):
    """ 表示順序で並べた後、公開期間で降順
    """
    return qs.order_by(sa.asc(cls.display_order),
                       sa.desc(cls.publish_open_on), 
                       )
    
class AboutPublishMixin(object):
    """ 表示順序を定義可能なmodelが持つ
    """
    publish_open_on = sa.Column(sa.DateTime)
    publish_close_on = sa.Column(sa.DateTime)
    display_order = sa.Column(sa.Integer, default=50)
    is_vetoed = sa.Column(sa.Boolean, default=False)
    
    @classmethod
    def publishing(cls, d=None, qs=None):
        if d is None:
            d = datetime.now()
        if qs is None:
            qs = cls.query
        return qs_has_permission(cls, qs_orderby_logic(cls, qs_in_term(cls, qs, d)))

_where = object()


def update_object_tag(obj, tagclass, ks, split_rx=re.compile("[,、]")):
    ## 面倒なのでO(N)
    splitted = obj.SPLIT_RX.split(ks)
    ks = set(k.strip() for k in splitted)
    will_updates = []
    for k in ks:
        if k: 
            tag = tagclass.query.filter_by(label=k, organization_id=obj.organization_id).first()
            tag = tag or tagclass(label=k, organization_id=obj.organization_id)
            will_updates.append(tag)
    will_deletes = set(obj.tags).difference(will_updates)
    for k in will_updates:
        obj.tags.append(k)
    for k in will_deletes:
        obj.tags.remove(k)

class TopicTag2Topic(Base):
    __tablename__ = "topictag2topic"
    id = sa.Column(sa.Integer, primary_key=True)
    query = DBSession.query_property()
    object_id = sa.Column(sa.Integer, sa.ForeignKey("topic.id"))
    tag_id = sa.Column(sa.Integer, sa.ForeignKey("topictag.id"))
topic2tag = TopicTag2Topic.__table__

class TopicTag(WithOrganizationMixin, Base):
    query = DBSession.query_property()
    __tablename__ = "topictag"
    id = sa.Column(sa.Integer, primary_key=True)
    label = sa.Column(sa.Unicode(255), index=True)
    publicp = sa.Column(sa.Boolean, default=False)
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now)
    @declared_attr
    def __tableargs__(cls):
        return  ((sa.schema.UniqueConstraint(cls.label,cls.organization_id)))        

    def __repr__(self):
        return "<%r label: %r organization_id: %r>" % (self.__class__, self.label, self.organization_id)

class Topic(AboutPublishMixin, 
            BaseOriginalMixin,
            WithOrganizationMixin, 
            Base):
    query = DBSession.query_property()

    __tablename__ = "topic"

    id = sa.Column(sa.Integer, primary_key=True)
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now)
    tags = orm.relationship("TopicTag", secondary=topic2tag, backref=orm.backref("topics"))

    title = sa.Column(sa.Unicode(255))
    text = sa.Column(sa.UnicodeText)
    
    ## topic をlinkとして利用したときの飛び先
    linked_page_id = sa.Column(sa.Integer, sa.ForeignKey("pagesets.id"), nullable=True)
    linked_page = orm.relationship(PageSet, primaryjoin="Topic.linked_page_id==PageSet.id")

    link = sa.Column(sa.Unicode(255), doc="external link", nullable=True)
    mobile_link = sa.Column(sa.Unicode(255), doc="external mobile_link", nullable=True)

    @property
    def tag_content(self):
        return u", ".join(k.label for k in self.tags)

    @tag_content.setter
    def tag_content(self, v):
        self._tag_content = v

    @classmethod
    def matched_qs(cls, d=None, tag=None, qs=None):
        qs = cls.publishing(d=d, qs=qs)
        if tag:
            qs = qs.filter(cls.tags.any(TopicTag.label==tag))

        return qs

    SPLIT_RX = re.compile("[,、]")
    def update_tag(self, ks):
        return update_object_tag(self, TopicTag, ks, self.SPLIT_RX)

def delete_topic_orphan_tag(mapper, connection, target):
    TopicTag.query.filter(~TopicTag.topics.any()).delete(synchronize_session=False)

sa.event.listen(Topic, "after_delete", delete_topic_orphan_tag)


class TopcontentTag2Topcontent(Base):
    __tablename__ = "topcontenttag2topcontent"
    id = sa.Column(sa.Integer, primary_key=True)
    query = DBSession.query_property()
    object_id = sa.Column(sa.Integer, sa.ForeignKey("topcontent.id"))
    tag_id = sa.Column(sa.Integer, sa.ForeignKey("topcontenttag.id"))
topcontent2tag = TopcontentTag2Topcontent.__table__

class TopcontentTag(WithOrganizationMixin, Base):
    query = DBSession.query_property()
    __tablename__ = "topcontenttag"
    id = sa.Column(sa.Integer, primary_key=True)
    label = sa.Column(sa.Unicode(255), index=True)
    publicp = sa.Column(sa.Boolean, default=False)
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now)
    @declared_attr
    def __tableargs__(cls):
        return  ((sa.schema.UniqueConstraint(cls.label,cls.organization_id)))        

    def __repr__(self):
        return "<%r label: %r organization_id: %r>" % (self.__class__, self.label, self.organization_id)

class Topcontent(AboutPublishMixin,
                 BaseOriginalMixin,
                 WithOrganizationMixin, 
                 Base):
    """
    Topページの画像つきtopicのようなもの
    """
    __tablename__ = "topcontent"
    query = DBSession.query_property()
    COUNTDOWN_CANDIDATES = h.base.COUNTDOWN_TAG_MAPPING.items()

    id = sa.Column(sa.Integer, primary_key=True)
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now)
    tags = orm.relationship("TopcontentTag", secondary=topcontent2tag, backref=orm.backref("topcontents"))

    title = sa.Column(sa.Unicode(255))
    text = sa.Column(sa.Unicode(255))

    ## topcontent をlinkとして利用したときの飛び先
    linked_page_id = sa.Column(sa.Integer, sa.ForeignKey("pagesets.id"), nullable=True)
    linked_page = orm.relationship(PageSet)

    link = sa.Column(sa.Unicode(255), doc="external link")
    mobile_link = sa.Column(sa.Unicode(255), doc="external mobile_link")

    ## extend
    image_asset_id = sa.Column(sa.Integer, sa.ForeignKey("image_asset.id"), nullable=True)
    image_asset = orm.relationship(ImageAsset, primaryjoin="Topcontent.image_asset_id==ImageAsset.id")
    mobile_image_asset_id = sa.Column(sa.Integer, sa.ForeignKey("image_asset.id"), nullable=True)
    mobile_image_asset = orm.relationship(ImageAsset, primaryjoin="Topcontent.mobile_image_asset_id==ImageAsset.id")
    countdown_type = sa.Column(sa.String(255)) #todo: fixme

    @property
    def tag_content(self):
        return u", ".join(k.label for k in self.tags)

    @tag_content.setter
    def tag_content(self, v):
        self._tag_content = v

    @property
    def countdown_type_ja(self):
        return h.base.countdown_tag_ja(self.countdown_type)

    @property
    def countdown_limit(self):
        return getattr(self.linked_page.event, self.countdown_type)

    @classmethod
    def matched_qs(cls, d=None, tag=None, qs=None):
        qs = cls.publishing(d=d, qs=qs)
        if tag:
            qs = qs.filter(cls.tags.any(TopcontentTag.label==tag))

        return qs

    SPLIT_RX = re.compile("[,、]")
    def update_tag(self, ks):
        return update_object_tag(self, TopcontentTag, ks, self.SPLIT_RX)


### promotion
class PromotionTag2Promotion(Base):
    __tablename__ = "promotiontag2promotion"
    id = sa.Column(sa.Integer, primary_key=True)
    query = DBSession.query_property()
    object_id = sa.Column(sa.Integer, sa.ForeignKey("promotion.id"))
    tag_id = sa.Column(sa.Integer, sa.ForeignKey("promotiontag.id"))
promotion2tag = PromotionTag2Promotion.__table__

class PromotionTag(WithOrganizationMixin, Base):
    query = DBSession.query_property()
    __tablename__ = "promotiontag"
    id = sa.Column(sa.Integer, primary_key=True)
    label = sa.Column(sa.Unicode(255), index=True)
    publicp = sa.Column(sa.Boolean, default=False)
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now)
    @declared_attr
    def __tableargs__(cls):
        return  ((sa.schema.UniqueConstraint(cls.label,cls.organization_id)))        

    def __repr__(self):
        return "<%r label: %r organization_id: %r>" % (self.__class__, self.label, self.organization_id)

class Promotion(WithOrganizationMixin, 
                AboutPublishMixin,
                Base):
    INTERVAL_TIME = 5000

    query = DBSession.query_property()
    __tablename__ = "promotion"

    id = sa.Column(sa.Integer, primary_key=True)
    tags = orm.relationship("PromotionTag", secondary=promotion2tag, 
                             backref=orm.backref("promotions"))
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now)

    main_image_id = sa.Column(sa.Integer, sa.ForeignKey("image_asset.id"))
    main_image = orm.relationship("ImageAsset", uselist=False, primaryjoin="Promotion.main_image_id==ImageAsset.id")
    text = sa.Column(sa.UnicodeText, default=u"no message")

    ## linkとpagesetは排他的
    link = sa.Column(sa.Unicode(255), nullable=True)
    linked_page_id = sa.Column(sa.Integer, sa.ForeignKey("pagesets.id"), nullable=True)
    linked_page = orm.relationship("PageSet")

    def validate(self):
        return self.pageset or self.link

    def to_dict(self):
        D = model_to_dict(self)
        D["tag_content"] = self.tag_content
        return D

    @property
    def tag_content(self):
        return u", ".join(k.label for k in self.tags)

    @tag_content.setter
    def tag_content(self, v):
        self._tag_content = v  

    @classmethod
    def matched_qs(cls, d=None, tag=None, qs=None):
        qs = cls.publishing(d=d, qs=qs)
        if tag:
            qs = qs.filter(cls.tags.any(PromotionTag.label==tag))

        return qs

    SPLIT_RX = re.compile("[,、]")
    def update_tag(self, ks):
        return update_object_tag(self, PromotionTag, ks, self.SPLIT_RX)

def delete_orphan_tag(mapper, connection, target):
    PromotionTag.query.filter(~PromotionTag.promotions.any()).delete(synchronize_session=False)

sa.event.listen(Promotion, "after_delete", delete_orphan_tag)
