from altaircms.models import DBSession
from altaircms.page.models import Page
from altaircms.event.models import Event
from altaircms.asset.models import Asset
from altaircms.asset.models import ImageAsset
from altaircms.asset.models import MovieAsset
from altaircms.asset.models import FlashAsset
from altaircms.tag import models as m

class TagManager(object):
    def __init__(self, Object, XRef, Tag):
        self.Object = Object
        self.XRef = XRef
        self.Tag = Tag

    @classmethod
    def page(cls):
        return cls(Page, m.PageTag2Page, m.PageTag)
    @classmethod
    def event(cls):
        return cls(Event, m.EventTag2Event, m.EventTag)
    @classmethod
    def asset(cls):
        return cls(Asset, m.AssetTag2Asset, m.AssetTag)
    @classmethod
    def image_asset(cls):
        return cls(ImageAsset, m.AssetTag2Asset, m.ImageAssetTag)
    @classmethod
    def movie_asset(cls):
        return cls(MovieAsset, m.AssetTag2Asset, m.MovieAssetTag)
    @classmethod
    def flash_asset(cls):
        return cls(FlashAsset, m.AssetTag2Asset, m.FlashAssetTag)

    def find_or_create_tag(self, obj, label):
        qs = self.Tag.query.filter_by(label=label)\
            .filter(self.Tag.pages.any(self.Object.id==obj.id))
        tag = qs.first()
        if not tag:
            self.Tag(label=label), True
        return tag, False

    def query(self, result=None):
        result = result or [self.Object]
        qs = DBSession.query(*result).filter(self.Object.id==self.XRef.object_id)
        return qs.filter(self.Tag.id==self.XRef.tag_id)

    def search(self, label, result=None):
        return self.query(result).filter(self.Tag.label==label)

    
