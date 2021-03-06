from altaircms.event.models import Event
from altaircms.page.models import PageSet, PageTag2Page, PageTag
from altaircms.page.models import MobileTag, MobileTag2Page

import logging
logger = logging.getLogger(__file__)

def log_debug(key, msg):
    logger.debug("*" + key + "* : " + msg)

def log_info(key, msg):
    logger.info("*" + key + "* : " + msg)

def log_warn(key, msg):
    logger.warning("*" + key + "* : " + msg)

def log_exception(key, msg):
    logger.exception("*" + key + "* : " + msg)

def log_error(key, msg):
    logger.error("*" + key + "* : " + msg)

class EventHelper(object):

    @classmethod
    def get_event_from_linked_page_id(cls, request, linked_page_id):
        log_info("get_event_from_linked_page_id", "start")
        event = request.allowable(Event) \
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

    @classmethod
    def get_summary_salessegment_group(cls, event):
        groups = []
        for group in event.salessegment_groups:
            start = None
            end = None
            salessegment_public = False
            for segment in group.salessegments:
                if not segment.publicp or not segment.performance.public:
                    continue

                salessegment_public = True

                if not start:
                    start = segment.start_on

                if not end:
                    end = segment.end_on

                if segment.start_on:
                    if start > segment.start_on:
                        start = segment.start_on

                if segment.end_on:
                    if end < segment.end_on:
                        end = segment.end_on

            if group.publicp and salessegment_public and start:
                groups.append(dict(group_name=group.name, start=start, end=end))
        return groups
