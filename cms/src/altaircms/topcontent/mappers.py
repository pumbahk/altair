from bpmappers import Mapper
import bpmappers.fields as fields


class TopcontentMapper(Mapper):
    def _ensure_timeformat(self, value):
        return value.isoformat()

    def after_filter_publish_at(self, value):
        return self._ensure_timeformat(value)

    id = fields.RawField()
    kind = fields.RawField()
    title = fields.RawField()
    text = fields.RawField()
    orderno = fields.RawField()
    is_vetoed = fields.RawField()

    publish_open_on = fields.RawField()
    publish_close_on = fields.RawField()
    page = fields.RawField()
    event = fields.RawField()
    is_global = fields.RawField()

class TopcontentsMapper(Mapper):
    topcontents = fields.ListDelegateField(TopcontentMapper)
