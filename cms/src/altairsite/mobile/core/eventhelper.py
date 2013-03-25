from altaircms.event.models import Event
from altaircms.page.models import PageSet, PageTag2Page, PageTag
from altairsite.mobile.core.helper import log_info

class EventHelper(object):

    @classmethod
    def get_event_from_promotion(cls, request, promotion):
        log_info("get_event_from_promotion", "start")
        event = request.allowable(Event) \
            .filter(Event.is_searchable == True) \
            .join(PageSet, Event.id == PageSet.event_id) \
            .filter(PageSet.id == promotion.linked_page_id).first()
        log_info("get_event_from_promotion", "end")
        return event

    @classmethod
    def get_event_from_topic(cls, request, topic):
        log_info("get_event_from_topic", "start")
        event = request.allowable(Event) \
            .filter(Event.is_searchable == True) \
            .join(PageSet, Event.id == PageSet.event_id) \
            .filter(PageSet.id == topic.linked_page_id).first()
        log_info("get_event_from_topic", "end")
        return event

    @classmethod
    def get_events_from_hotword(cls, request, hotword):
        log_info("get_event_from_hotword", "start")
        events = request.allowable(Event) \
            .filter(Event.is_searchable == True) \
            .join(PageSet, Event.id == PageSet.event_id) \
            .join(PageTag2Page, PageSet.id == PageTag2Page.object_id) \
            .join(PageTag, PageTag2Page.tag_id == PageTag.id) \
            .filter(PageTag.id == hotword.tag_id).all()
        log_info("get_event_from_hotword", "end")
        return events
