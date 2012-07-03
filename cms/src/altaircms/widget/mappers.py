# coding: utf-8
from bpmappers.fields import RawField, DelegateField, NonKeyField, NonKeyDelegateField
from bpmappers.mappers import Mapper

from altaircms.asset.mappers import ImageAssetMapper, FlashAssetMapper, MovieAssetMapper

class BaseWidgetMapper(Mapper):
    id = RawField()
    organization_id = RawField()
    # type = RawField()

    
class TextWidgetMapper(BaseWidgetMapper):
    text = RawField()


class ImageWidgetMapper(BaseWidgetMapper):
    asset = DelegateField(ImageAssetMapper)
    asset_id = RawField()


class MovieWidgetMapper(BaseWidgetMapper):
    asset = DelegateField(MovieAssetMapper)
    asset_id = RawField()


class FlashWidgetMapper(BaseWidgetMapper):
    asset =DelegateField(FlashAssetMapper)
    asset_id = RawField()


class MenuWidgetMapper(BaseWidgetMapper):
    menu = RawField()


class BreadcrumbsWidgetMapper(BaseWidgetMapper):
    breadcrumb = RawField()


class TopicWidgetMapper(BaseWidgetMapper):
    topic_id = RawField()
    title = RawField()
