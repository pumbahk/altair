from bpmappers import Mapper
import bpmappers.fields as fields


class TopicMapper(Mapper):
    id = fields.RawField()
    event = fields.RawField()
    title = fields.RawField()
    text = fields.RawField()
    # client_id = fields.RawField()  # fixme: need delegate?

class TopicsMapper(Mapper):
    topics = fields.ListDelegateField(TopicMapper)
