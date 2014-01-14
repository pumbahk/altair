# -*- coding:utf-8 -*-
import re
import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.ext.declarative import declared_attr
from datetime import datetime

from altaircms.models import Base
from altaircms.models import DBSession, model_to_dict
from altaircms.page.models import PageSet
from altaircms.asset.models import ImageAsset
from altaircms.models import WithOrganizationMixin, Genre


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
    
class TopicCore(Base):
    """ 表示順序を定義可能なmodel.(歴史的理由によりTopicCoreの特殊化したものがTopic, Topcontent, Promotion)
    """
    __tablename__ = "topiccore"
    query = DBSession.query_property()

    id = sa.Column(sa.Integer, primary_key=True)
    publish_open_on = sa.Column(sa.DateTime)
    publish_close_on = sa.Column(sa.DateTime)
    display_order = sa.Column(sa.Integer, default=50)
    is_vetoed = sa.Column(sa.Boolean, default=False)
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now)
    discriminator = sa.Column("type", sa.String(32), nullable=False)
    __mapper_args__ = {"polymorphic_on": discriminator}

    @classmethod
    def order_by_logic(cls, qs=None):
        if qs is None:
            qs = cls.query
        return qs_orderby_logic(cls, qs)

    @classmethod
    def publishing(cls, d=None, qs=None):
        if d is None:
            d = datetime.now()
        if qs is None:
            qs = cls.query
        return qs_has_permission(cls, qs_orderby_logic(cls, qs_in_term(cls, qs, d)))

    def to_dict(self):
        D = model_to_dict(self)
        D["tag_content"] = self.tag_content
        D["genre"] = self.genre_id_list_from_topic()
        return D

    @property
    def topic_kinds(self):
        """''注目のイベント''など種別で絞り込む"""
        organization_id = self.organization_id
        return (k for k in self.tags if k.publicp and k.organization_id == organization_id)

    @property
    def topic_genres(self):
        """所属しているジャンル一覧"""
        #今のところorganization_id=Noneのタグ(system tag)はジャンルに使われている
        return (k for k in self.tags if k.organization_id is None)

    ## theese are hack. so, sorry(in slackoff view)
    @property
    def tag_content(self):
        return [tag.label for tag in self.topic_kinds]

    @tag_content.setter
    def tag_content(self, v):
        self._tag_content = v  
    
    def genre_id_list_from_topic(self):
        labels = []
        for t in self.tags:
            if t.organization_id is None:
                labels.append(t.label)
        pks = Genre.query.filter_by(organization_id=self.organization_id)\
            .filter(Genre.label.in_(labels)).with_entities(Genre.id).all()
        return [pk for xs in pks for pk in xs]
        
        
    @property
    def genre(self):
        return u", ".join(k.label for k in self.topic_genres)
    
    @genre.setter
    def genre(self, vs):
        self._genre = vs

    def delete(self, session=None):
        tags = list(self.tags)
        for t in tags:
            self.tags.remove(t)
        
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


class Topic(WithOrganizationMixin, TopicCore):
    type = "topic"
    
    __tablename__ = "topic"
    __mapper_args__ = {"polymorphic_identity": type}

    id = sa.Column(sa.Integer, sa.ForeignKey("topiccore.id"), primary_key=True)
    title = sa.Column(sa.Unicode(255))
    text = sa.Column(sa.UnicodeText)
    
    ## topic をlinkとして利用したときの飛び先
    linked_page_id = sa.Column(sa.Integer, sa.ForeignKey("pagesets.id"), nullable=True)
    linked_page = orm.relationship(PageSet, primaryjoin="Topic.linked_page_id==PageSet.id")

    link = sa.Column(sa.Unicode(255), doc="external link", nullable=True)
    mobile_link = sa.Column(sa.Unicode(255), doc="external mobile_link", nullable=True)
    tags = orm.relationship("TopicTag", secondary="topiccoretag2topiccore", backref=orm.backref("topics"))
    mobile_tag = orm.relationship("MobileTag", uselist=False, backref="topics")
    mobile_tag_id = sa.Column(sa.Integer, sa.ForeignKey("mobiletag.id"))

    @classmethod
    def matched_qs(cls, d=None, tag=None, qs=None):
        qs = cls.publishing(d=d, qs=qs)
        if tag:
            qs = qs.filter(cls.tags.any(TopicTag.label==tag))
        return qs

_COUNTDOWN_TYPE_MAPPING = dict(
    event_open=u"公演開始", 
    event_close=u"公演終了", 
    deal_open=u"販売開始", 
    deal_close=u"販売終了")

class Topcontent(WithOrganizationMixin, TopicCore):
    """
    Topページの画像つきtopicのようなもの
    """
    type = "topcontent"
    
    __tablename__ = "topcontent"
    __mapper_args__ = {"polymorphic_identity": type}
    COUNTDOWN_TYPE_MAPPING = _COUNTDOWN_TYPE_MAPPING
    COUNTDOWN_CANDIDATES = COUNTDOWN_TYPE_MAPPING.items()

    id = sa.Column(sa.Integer, sa.ForeignKey("topiccore.id"), primary_key=True)
    tags = orm.relationship("TopcontentTag", secondary="topiccoretag2topiccore", backref=orm.backref("topcontents"))

    mobile_tag = orm.relationship("MobileTag", uselist=False, backref="topcontents")
    mobile_tag_id = sa.Column(sa.Integer, sa.ForeignKey("mobiletag.id"))

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
    def countdown_type_ja(self):
        return self.COUNTDOWN_TYPE_MAPPING.get(self.countdown_type, u"")

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

class Promotion(WithOrganizationMixin, TopicCore):
    type = "promotion"
    
    __tablename__ = "promotion"
    __mapper_args__ = {"polymorphic_identity": type}

    id = sa.Column(sa.Integer, sa.ForeignKey("topiccore.id"), primary_key=True)
    mobile_tag = orm.relationship("MobileTag", uselist=False, backref="promotions")
    tags = orm.relationship("PromotionTag", secondary="topiccoretag2topiccore",
                             backref=orm.backref("promotions"))
    main_image_id = sa.Column(sa.Integer, sa.ForeignKey("image_asset.id"))
    main_image = orm.relationship("ImageAsset", uselist=False, primaryjoin="Promotion.main_image_id==ImageAsset.id")
    text = sa.Column(sa.UnicodeText, default=u"no message")
    mobile_tag_id = sa.Column(sa.Integer, sa.ForeignKey("mobiletag.id"))

    ## linkとpagesetは排他的
    link = sa.Column(sa.Unicode(255), nullable=True)
    mobile_link = sa.Column(sa.Unicode(255), nullable=True)
    linked_page_id = sa.Column(sa.Integer, sa.ForeignKey("pagesets.id"), nullable=True)
    linked_page = orm.relationship("PageSet")

    def validate(self):
        return self.pageset or self.link

    @classmethod
    def matched_qs(cls, d=None, tag=None, qs=None):
        qs = cls.publishing(d=d, qs=qs)
        if tag:
            qs = qs.filter(cls.tags.any(PromotionTag.label==tag))

        return qs

    SPLIT_RX = re.compile("[,、]")
    def update_tag(self, ks):
        return update_object_tag(self, PromotionTag, ks, self.SPLIT_RX)
## tag

class TopicCoreTag2TopicCore(Base):
    __tablename__ = "topiccoretag2topiccore"
    object_id = sa.Column(sa.Integer, sa.ForeignKey("topiccore.id"), primary_key=True)
    tag_id = sa.Column(sa.Integer, sa.ForeignKey("topiccoretag.id"), primary_key=True)
    topic = orm.relationship("Topic", backref=orm.backref("topictag2topic", cascade="all, delete-orphan"))

    __tableargs__ = (
        sa.UniqueConstraint("object_id", "tag_id") #todo.delete id. and this unique constraint
        )
topiccoretag2topiccore = TopicCoreTag2TopicCore.__table__


"""
organization_id == NULLのデータはmasterデータ。
"""
class TopicCoreTag(WithOrganizationMixin, Base):
    CLASSIFIER = "topiccore"
    
    __tablename__ = "topiccoretag"
    id = sa.Column(sa.Integer, primary_key=True)
    query = DBSession.query_property()
    label = sa.Column(sa.Unicode(255), index=True)
    topiccores = orm.relationship("TopicCore", secondary="topiccoretag2topiccore")
    publicp = sa.Column(sa.Boolean, default=False)
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now)
    # usecase = sa.Column(sa.Enum(*TOPIC_TAG_USECASE_LIST), default="normal")
    discriminator = sa.Column("type", sa.String(32), nullable=False)
    __mapper_args__ = {"polymorphic_on": discriminator}

    def __repr__(self):
        return "<%r label: %r organization_id: %r>" % (self.__class__, self.label, self.organization_id)

# def delete_orphan_topiccoretag(mapper, connection, target):
#     TopicCoreTag.query.filter(~TopicCoreTag.topiccores.any()).delete(synchronize_session=False)
# sa.event.listen(TopicCore, "after_delete", delete_orphan_topiccoretag)

class TopicTag(TopicCoreTag):
    type = "topic"
    __mapper_args__ = {"polymorphic_identity": type}
    @declared_attr
    def __tableargs__(cls):
        return  ((sa.schema.UniqueConstraint(cls.label, cls.discriminator, cls.organization_id, cls.publicp)))        
# def delete_orphan_tag(mapper, connection, target):
#     TopicTag.query.filter(~TopicTag.topiccores.any()).delete(synchronize_session=False)
# sa.event.listen(Topic, "after_delete", delete_orphan_tag)

class TopcontentTag(TopicCoreTag):
    type = "topcontent"
    __mapper_args__ = {"polymorphic_identity": type}
    @declared_attr
    def __tableargs__(cls):
        return  ((sa.schema.UniqueConstraint(cls.label, cls.discriminator, cls.organization_id)))        
# def delete_orphan_tag(mapper, connection, target):
#     TopcontentTag.query.filter(~TopcontentTag.topiccores.any()).delete(synchronize_session=False)
# sa.event.listen(Topcontent, "after_delete", delete_orphan_tag)


class PromotionTag(TopicCoreTag):
    type = "promotion"
    __mapper_args__ = {"polymorphic_identity": type}
    @declared_attr
    def __tableargs__(cls):
        return  ((sa.schema.UniqueConstraint(cls.label, cls.discriminator, cls.organization_id)))        

# def delete_orphan_tag(mapper, connection, target):
#     PromotionTag.query.filter(~PromotionTag.topiccores.any()).delete(synchronize_session=False)
# sa.event.listen(Promotion, "after_delete", delete_orphan_tag)
