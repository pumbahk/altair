# -*- encoding:utf-8 -*-

from zope.interface import implementer
from altaircms.interfaces import IModelEvent
from altaircms.page.api import ftsearch_register_from_page
from altaircms.page.api import get_static_page_utility
from altaircms.models import SalesSegmentGroup, DBSession
from altaircms.modelmanager import SalesTermSummalize
from altaircms.modelmanager import EventTermSummalize
from altaircms.page.staticupload.creation import AfterDeleteCompletely

def notify_topic_create(request, topic, params=None):
    registry = request.registry
    return registry.notify(TopicCreate(request, topic, params))

def notify_topic_update(request, topic, params=None):
    registry = request.registry
    return registry.notify(TopicUpdate(request, topic, params))

def notify_topic_delete(request, topic, params=None):
    registry = request.registry
    return registry.notify(TopicDelete(request, topic, params))


class ModelEventBase(object):
    def __init__(self, request, obj, params=None):
        self.request = request
        self.obj = obj
        self.params = params

@implementer(IModelEvent)
class TopicCreate(ModelEventBase):
    pass

@implementer(IModelEvent)
class TopicUpdate(ModelEventBase):
    pass
        
@implementer(IModelEvent)
class TopicDelete(ModelEventBase):
    pass

@implementer(IModelEvent)
class PageSetUpdate(ModelEventBase):
    pass

@implementer(IModelEvent)
class PerformanceCreate(ModelEventBase):
    pass

@implementer(IModelEvent)
class PerformanceUpdate(ModelEventBase):
    pass

@implementer(IModelEvent)
class SalesSegmentCreate(ModelEventBase):
    pass

@implementer(IModelEvent)
class SalesSegmentUpdate(ModelEventBase):
    pass

@implementer(IModelEvent)
class TicketCreate(ModelEventBase):
    pass

@implementer(IModelEvent)
class TicketUpdate(ModelEventBase):
    pass

@implementer(IModelEvent)
class StaticPageSetUpdate(ModelEventBase):
    pass

@implementer(IModelEvent)
class StaticPageSetDelete(ModelEventBase):
    pass


## need async
##
from altaircms.tag.api import put_tags, put_mobile_tags, tags_from_string, put_system_tags
from altaircms.models import Genre

def tags_from_value(v):
    if isinstance(v, (list, tuple)):
        return tags_from_string(u",".join(v), separator=u",")
    else:
        return tags_from_string(v, separator=u",")

def _tag_labels_from_genres(genres):
    S = set()
    for g in genres:
        for c in g.ancestors:
            S.add(c.label)
    return list(S)
    

def update_kind(self):
    tag_labels = tags_from_value(self.params["tag_content"])
    obj_type = self.obj.__tablename__
    put_tags(self.obj, obj_type, tag_labels, [], self.request)

    genres = Genre.query.filter(Genre.id.in_(self.params["genre"])).all()
    system_tag_labels = _tag_labels_from_genres(genres)
    put_system_tags(self.obj, obj_type, system_tag_labels, self.request)


def update_pageset_genretag(self):
    pageset = self.obj
    page = self.obj.pages[0]

    tags = tags_from_value(self.params["tags_string"])
    private_tags = tags_from_value(self.params["private_tags_string"])
    mobile_tags = tags_from_value(self.params["mobile_tags_string"])
    obj_type = "page"
    mobile_obj_type = "mobilepage"
    put_tags(pageset, obj_type, tags, private_tags, self.request)
    put_mobile_tags(pageset, mobile_obj_type, mobile_tags, self.request)
    ftsearch_register_from_page(self.request, page)
    if self.params.get("genre_id"):
        genres = Genre.query.filter(Genre.id == self.params["genre_id"]).all()
        system_tag_labels = _tag_labels_from_genres(genres)
        put_system_tags(pageset, obj_type, system_tag_labels, self.request)
    else:
        pageset.kick_genre()
    if pageset.pagetype.is_portal and pageset.genre and self.request.params['endpoint'].find('page_separation') == -1:
        DBSession.flush()
        pageset.genre.save_as_category_toppage(pageset)

def update_page_genretag(self):
    pageset = self.obj.pageset
    page = self.obj

    tags = tags_from_value(self.params["tags"])
    private_tags = tags_from_value(self.params["private_tags"])
    mobile_tags = tags_from_value(self.params["mobile_tags"])
    obj_type = "page"
    mobile_obj_type = "mobilepage"
    put_tags(pageset, obj_type, tags, private_tags, self.request)
    put_mobile_tags(pageset, mobile_obj_type, mobile_tags, self.request)
    ftsearch_register_from_page(self.request, page)
    if self.params.get("genre"):
        genres = [self.params["genre"]]
        system_tag_labels = _tag_labels_from_genres(genres)
        put_system_tags(pageset, obj_type, system_tag_labels, self.request)

    if pageset.pagetype.is_portal and pageset.genre:
        DBSession.flush()
        pageset.genre.save_as_category_toppage(pageset)

def create_salessegment_group(self):
    event = self.params["event"]
    if not event.salessegment_groups:
        DBSession.add_all(SalesSegmentGroup.create_defaults_from_event(event))
        
def sales_term_bubbling_update(self):
    SalesTermSummalize(self.request).summalize(self.obj).bubble()

def event_term_bubbling_update(self):
    EventTermSummalize(self.request).summalize(self.obj).bubble()

def after_delete_static_pageset(self):
    for p in self.obj.pages:
        DBSession.delete(p)
    utility = get_static_page_utility(self.request)
    self.request.registry.notify(AfterDeleteCompletely(self.request, utility, self.obj))

def after_change_ticket(self):
    if self.obj.seattype is None:
        self.obj.seattype = u""
