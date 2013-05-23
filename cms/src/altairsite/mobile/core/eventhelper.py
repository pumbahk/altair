from altaircms.event.models import Event
from altaircms.page.models import PageSet, PageTag2Page, PageTag
from altairsite.mobile.core.helper import log_info
from altaircms.page.models import MobileTag, MobileTag2Page

class EventHelper(object):

    @classmethod
    def get_event_from_linked_page_id(cls, request, linked_page_id):
        log_info("get_event_from_linked_page_id", "start")
        event = request.allowable(Event) \
            .filter(Event.is_searchable == True) \
            .join(PageSet, Event.id == PageSet.event_id) \
            .filter(PageSet.id == linked_page_id).first()
        log_info("get_event_from_linked_page_id", "end")
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

    @classmethod
    def get_eventsqs_from_mobile_tag_id(cls, request, mobile_tag_id):
        log_info("get_events_from_mobile_tag_id", "start")
        qs = request.allowable(Event) \
            .filter(Event.is_searchable == True) \
            .join(PageSet, Event.id == PageSet.event_id) \
            .join(MobileTag2Page, PageSet.id == MobileTag2Page.object_id) \
            .join(MobileTag, MobileTag2Page.tag_id == MobileTag.id) \
            .filter(MobileTag.id == mobile_tag_id)
        log_info("get_events_from_mobile_tag_id", "start")
        return qs