# -*- coding:utf-8 -*-
from altaircms.models import DBSession
import sqlalchemy.orm as orm
import sqlalchemy.sql.expression as saexp
from zope.interface import implementer
from .interfaces import ITagManager
from .interfaces import ISystemTagManager
import re

class QueryParser(object):
    """ support and search only
    e.g. "abc def" => a object has abc and def.
    """
    def __init__(self, query):
        self.query = query

    def parse(self):
        words = re.split(u"[, 　\s]+", self.query.strip())
        return [x for x in words if x]

    def and_search_by_manager(self, manager):
        words = self.parse()
        word_count = len(words)
        if word_count <= 0:
            return manager.Object.query
        elif word_count <= 1:
            return manager.search_by_tag_label(words[0])
        else:
            where = manager.Object.tags.any(label=words[0])
            for w in words[1:]:
                where = where & (manager.Object.tags.any(label=w))
            return manager.joined_query().filter(where)

"""
todo. refactoring. 継承が良いわけない
"""

class TagManagerBase(object):
    def __init__(self, Object, XRef, Tag):
        self.Object = Object
        self.XRef = XRef
        self.Tag = Tag

    def get_tag_list(self, labels, public_status=None, organization_id=None):
        qs = self.Tag.query.filter(self.Tag.label.in_(labels), organization_id=organization_id)
        if public_status is not None:
            qs = qs.filter(self.Tag.publicp==public_status)
        return qs.all()

    def get_or_create_tag_list(self, labels, public_status=True, organization_id=None):
        tags = self.get_tag_list(labels, public_status=public_status, organization_id=organization_id)
        cache = {tag.label:tag for tag in tags}
        result = []
        for label in labels:
            if not label in cache:
                result.append(self.Tag(label=label, publicp=public_status, organization_id=organization_id))
            else:
                result.append(cache[label])
        return result
            
    def get_or_create_tag(self, label, public_status=True, organization_id=None):
        tag = self.Tag.query.filter_by(label=label, publicp=public_status, organization_id=organization_id).first()
        if not tag:
            return self.Tag(label=label, publicp=public_status, organization_id=organization_id)
        else:
            return tag

    def public_search_by_tag_label(self, label):
        return self.search_by_tag_label(label).filter(self.Tag.publicp==True)

    def private_search_by_tag_label(self, label):
        return self.search_by_tag_label(label).filter(self.Tag.publicp==False)

    def search_by_tag_label(self, label):
        qs = self.joined_query([self.Object]).filter(self.Tag.label==label)
        return qs

    ## history
    def recent_change_tags(self):
        pass

    ## alter
    def delete_tags(self, obj, deletes, public_status=True, organization_id=None):
        """ deletes: [unicode]
        """
        if deletes:
            tags = obj.tags
            qs = self.Tag.query.filter(self.XRef.object_id==obj.id).filter(self.Tag.publicp == public_status)
            for tag in qs.filter(self.Tag.label.in_(deletes), organization_id=organization_id):
                tags.remove(tag)
        
    def replace_tags(self, obj, tag_label_list, public_status=True, organization_id=None):
        if obj.tags:
            return self.fullreplace_tags(obj, tag_label_list, public_status, organization_id=organization_id)
        else:
            return self.add_tags(obj, tag_label_list, public_status, organization_id=organization_id)


    def fullreplace_tags(self, obj, tag_label_list, public_status, organization_id=None):
        prev_name_set = set(x.label for x in obj.tags if x.publicp == public_status and x.organization_id==organization_id)
        deletes = prev_name_set.difference(tag_label_list)
        self.delete_tags(obj, deletes)
        updates = set(tag_label_list).difference(prev_name_set)

        result = []
        for label in updates:
            t = self.get_or_create_tag(label, public_status, organization_id=organization_id)
            result.append(t)
            obj.tags.append(t)
        return result

    def joined_query(self, query_target=None):
        pass

    def is_target_tag(self, tag):
        pass

    def search_by_tag(self, tag):
        return self.joined_query([self.Object]).filter(self.Tag.id==tag.id)

    def add_tags(self, obj, tag_label_list, public_status, organization_id=None):
        tags = obj.tags
        result = []
        for label in tag_label_list:
            t = self.get_or_create_tag(label, public_status, organization_id=organization_id)
            result.append(t)
            tags.append(t)
        return result

@implementer(ITagManager)
class TagManager(TagManagerBase):
    def is_target_tag(self, tag):
        return tag.organization_id is not None        

    def joined_query(self, query_target=None):
        query_target = query_target or [self.Object]
        qs = DBSession.query(*query_target).filter(self.Object.id==self.XRef.object_id)
        qs = qs.filter(self.Object.organization_id==self.Tag.organization_id)
        return qs.filter(self.Tag.id==self.XRef.tag_id)
        
    def more_filter_by_tag(self, qs, tag):
        xref = orm.aliased(self.XRef)
        qs = qs.filter(self.Object.id==xref.object_id, xref.tag_id==tag.id)
        qs = qs.filter(self.Object.organization_id==tag.organization_id)
        return qs

    def recent_change_tags(self):
        return self.Tag.query.filter(self.Tag.organization_id!=None).order_by(saexp.desc(self.Tag.updated_at), saexp.asc(self.Tag.id))

@implementer(ISystemTagManager)
class SystemTagManager(TagManagerBase):
    def is_target_tag(self, tag):
        return tag.organization_id is None        

    def joined_query(self, query_target=None):
        query_target = query_target or [self.Object]
        qs = DBSession.query(*query_target).filter(self.Object.id==self.XRef.object_id)
        qs = qs.filter(self.Tag.organization_id==None)
        return qs.filter(self.Tag.id==self.XRef.tag_id)

    def more_filter_by_tag(self, qs, tag):
        xref = orm.aliased(self.XRef)
        return qs.filter(self.Object.id==xref.object_id, xref.tag_id==tag.id).filter(self.Tag.organization_id==None)

    def recent_change_tags(self):
        return self.Tag.query.filter(self.Tag.organization_id==None).order_by(saexp.desc(self.Tag.updated_at), saexp.asc(self.Tag.id))
