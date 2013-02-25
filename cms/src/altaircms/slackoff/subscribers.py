# -*- encoding:utf-8 -*-

from zope.interface import implementer
from altaircms.interfaces import IModelEvent
from altaircms.page.api import ftsearch_register_from_page

def notify_topic_create(request, topic, params=None):
    registry = request.registry
    return registry.notify(TopicCreate(request, topic, params))

def notify_topic_update(request, topic, params=None):
    registry = request.registry
    return registry.notify(TopicUpdate(request, topic, params))

def notify_topic_delete(request, topic, params=None):
    registry = request.registry
    return registry.notify(TopicDelete(request, topic, params))


@implementer(IModelEvent)
class TopicCreate(object):
    def __init__(self, request, obj, params=None):
        self.request = request
        self.obj = obj
        self.params = params

@implementer(IModelEvent)
class TopicUpdate(object):
    def __init__(self, request, obj, params=None):
        self.request = request
        self.obj = obj
        self.params = params
        
@implementer(IModelEvent)
class TopicDelete(object):
    def __init__(self, request, obj, params=None):
        self.request = request
        self.obj = obj
        self.params = params

@implementer(IModelEvent)
class PageSetUpdate(object):
    def __init__(self, request, obj, params=None):
        self.request = request
        self.obj = obj
        self.params = params

## need async
##
from altaircms.tag.api import put_tags, tags_from_string, put_system_tags
from altaircms.models import Genre

def _tag_labels_from_genres(genres):
    S = set()
    for g in genres:
        S.add(g.label)
        for c in g.ancestors:
            S.add(c.label)
    return list(S)
    

def update_kind(self):
    tag_labels = tags_from_string(self.params["tag_content"])
    obj_type = self.obj.__tablename__
    put_tags(self.obj, obj_type, tag_labels, [], self.request)

    if self.params.get("genre"):
        genres = Genre.query.filter(Genre.id.in_(self.params["genre"])).all()
        system_tag_labels = _tag_labels_from_genres(genres)
        put_system_tags(self.obj, obj_type, system_tag_labels, self.request)

def update_pageset(self):
    tags = tags_from_string(self.params["tags_string"])
    private_tags = tags_from_string(self.params["private_tags_string"])
    obj_type = "page"
    put_tags(self.obj, obj_type, tags, private_tags, self.request)
    ftsearch_register_from_page(self.request, self.obj.pages[0])
    if self.params.get("genre_id"):
        genres = Genre.query.filter(Genre.id == self.params["genre_id"]).all()
        system_tag_labels = _tag_labels_from_genres(genres)
        put_system_tags(self.obj, obj_type, system_tag_labels, self.request)
    
