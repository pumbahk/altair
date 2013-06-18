
import sqlalchemy as sa
import sqlalchemy.orm as orm
import sqlalchemy.schema as saschema
from altaircms.models import Base
from altaircms.models import DBSession

from datetime import datetime
## backward compability
from altaircms.page.models import Page, PageTag, PageTag2Page
from altaircms.asset.models import Asset, AssetTag, AssetTag2Asset
from altaircms.asset.models import ImageAsset, ImageAssetTag
from altaircms.asset.models import MovieAsset, MovieAssetTag
from altaircms.asset.models import FlashAsset, FlashAssetTag
from altaircms.topic.models import TopicTag, TopicCoreTag2TopicCore, TopicCoreTag, TopcontentTag, PromotionTag
from altaircms.models import WithOrganizationMixin


class HotWord(WithOrganizationMixin, Base):
    query = DBSession.query_property()

    id = sa.Column(sa.Integer, primary_key=True)
    __tablename__ = "hotword"
    
    tag_id =  sa.Column(sa.Integer, sa.ForeignKey("pagetag.id"))
    tag = orm.relationship("PageTag", uselist=False, backref="hotwords")
    name = sa.Column(sa.Unicode(255))
    display_order = sa.Column(sa.Integer, default=100) # 0~100

    enablep = sa.Column(sa.Boolean, default=True)
    term_begin = sa.Column(sa.DateTime)
    term_end = sa.Column(sa.DateTime)

    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now)

    @classmethod
    def from_page(cls, page):
        qs = cls.query.filter(cls.tag_id==PageTag.id)
        qs = qs.filter(PageTag2Page.tag_id==PageTag.id).filter(PageTag2Page.object_id==Page.id)
        qs = qs.filter(Page.id==page.id)
        return qs
    
