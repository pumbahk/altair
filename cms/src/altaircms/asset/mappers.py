# coding: utf-8
from bpmappers.fields import RawField
from bpmappers.mappers import Mapper

class BaseAssetMapper(Mapper):
    id = RawField()
    site_id = RawField()
    mimetype = RawField()
    filepath = RawField()

class ImageAssetMapper(BaseAssetMapper):
    pass

class MovieAssetMapper(BaseAssetMapper):
    pass

class FlashAssetMapper(BaseAssetMapper):
    pass
