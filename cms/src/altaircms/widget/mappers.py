# coding: utf-8
from bpmappers.fields import RawField
from bpmappers.mappers import Mapper

class BaseWidgetMapper(Mapper):
    id = RawField()
    site_id = RawField()
    type = RawField()


class TextWidgetMapper(BaseWidgetMapper):
    text = RawField()


class ImageWidgetMapper(BaseWidgetMapper):
    asset_id = RawField()


class MovieWidgetMapper(BaseWidgetMapper):
    asset_id = RawField()


class FlashWidgetMapper(BaseWidgetMapper):
    asset_id = RawField()


class MenuWidgetMapper(BaseWidgetMapper):
    menu = RawField()


class BreadcrumbsWidgetMapper(BaseWidgetMapper):
    breadcrumb = RawField()


class TopicWidgetMapper(BaseWidgetMapper):
    topic_id = RawField()
    title = RawField()
