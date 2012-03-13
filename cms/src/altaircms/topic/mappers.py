from bpmappers import Mapper
import bpmappers.fields as fields


class TopicMapper(Mapper):
    def _ensure_timeformat(self, value):
        return value.isoformat()

    def after_filter_publish_at(self, value):
        return self._ensure_timeformat(value)

    id = fields.RawField()
    kind = fields.RawField()
    title = fields.RawField()
    text = fields.RawField()
    publish_at = fields.RawField()

class TopicsMapper(Mapper):
    topics = fields.ListDelegateField(TopicMapper)
