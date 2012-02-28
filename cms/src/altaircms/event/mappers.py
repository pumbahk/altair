# coding: utf-8
from bpmappers import Mapper
from bpmappers.fields import RawField, DelegateField, ListDelegateField

class EventMapper(Mapper):
    def _ensure_timeformat(self, value):
        return value.isoformat()

    def after_filter_event_open(self, value):
        return self._ensure_timeformat(value)

    def after_filter_event_close(self, value):
        return self._ensure_timeformat(value)

    def after_filter_deal_open(self, value):
        return self._ensure_timeformat(value)

    def after_filter_deal_close(self, value):
        return self._ensure_timeformat(value)

    def after_filter_id(self, value):
        return int(value)

    def after_filter_is_searchable(self, value):
        return True if value == 'y' else False

    id = RawField()
    title = RawField()
    subtitle = RawField()
    description = RawField()
    place = RawField()
    inquiry_for = RawField()
    event_open = RawField()
    event_close = RawField()
    deal_open = RawField()
    deal_close = RawField()
    is_searchable = RawField()
    client_id = RawField()  # delegateしたほうがいいかも


class EventsMapper(Mapper):
    events = ListDelegateField(EventMapper)
