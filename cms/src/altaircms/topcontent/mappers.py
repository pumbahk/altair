from bpmappers import Mapper
import bpmappers.fields as fields


class TopcontentMapper(Mapper):
    def _ensure_timeformat(self, value):
        return value.isoformat()

    def after_filter_publish_open_on(self, value):
        return self._ensure_timeformat(value)
    def after_filter_publish_close_on(self, value):
        return self._ensure_timeformat(value)

    id = fields.RawField()
    kind = fields.RawField()
    category = fields.RawField()
    title = fields.RawField()
    text = fields.RawField()
    orderno = fields.RawField()
    is_vetoed = fields.RawField()

    publish_open_on = fields.RawField()
    publish_close_on = fields.RawField()
    page = fields.RawField()
    # is_global = fields.RawField()
    image_asset = fields.RawField()
    countdown_type = fields.RawField()

class TopcontentsMapper(Mapper):
    topcontents = fields.ListDelegateField(TopcontentMapper)
