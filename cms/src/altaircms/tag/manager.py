from altaircms.models import DBSession
import sqlalchemy.sql.expression as saexp
from zope.interface import implementer
from .interfaces import ITagManager

@implementer(ITagManager)
class TagManager(object):
    def __init__(self, Object, XRef, Tag):
        self.Object = Object
        self.XRef = XRef
        self.Tag = Tag

    def get_or_create_tag(self, label, public_status=True):
        tag = self.Tag.query.filter_by(label=label, publicp=public_status).first()
        if not tag:
            return self.Tag(label=label, publicp=public_status)
        else:
            return tag

    ## search
    def joined_query(self, query_target=None):
        query_target = query_target or [self.Object]
        qs = DBSession.query(*query_target).filter(self.Object.id==self.XRef.object_id)
        return qs.filter(self.Tag.id==self.XRef.tag_id)

    def public_search_by_tag_label(self, label):
        return self.search_by_tag_label(label).filter(self.Tag.publicp==True)

    def private_search_by_tag_label(self, label):
        return self.search_by_tag_label(label).filter(self.Tag.publicp==False)

    def search_by_tag_label(self, label):
        return self.joined_query([self.Object]).filter(self.Tag.label==label)

    ## history
    def recent_change_tags(self):
        return self.Tag.query.order_by(saexp.desc(self.Tag.updated_at))

    ## alter
    def delete_tags(self, obj, deletes, public_status=True):
        """ deletes: [unicode]
        """
        if deletes:
            tags = obj.tags
            qs = self.Tag.query.filter(self.XRef.object_id==obj.id).filter(self.Tag.publicp == public_status)
            for tag in qs.filter(self.Tag.label.in_(deletes)):
                tags.remove(tag)
        
    def replace_tags(self, obj, tag_label_list, public_status=True):
        if obj.tags:
            return self.fullreplace_tags(obj, tag_label_list, public_status)
        else:
            return self.add_tags(obj, tag_label_list, public_status)

    def fullreplace_tags(self, obj, tag_label_list, public_status):
        prev_name_set = set(x.label for x in obj.tags if x.publicp == public_status)
        deletes = prev_name_set.difference(tag_label_list)
        self.delete_tags(obj, deletes)
        updates = set(tag_label_list).difference(prev_name_set)

        for label in updates:
            obj.tags.append(self.get_or_create_tag(label, public_status))

    def add_tags(self, obj, tag_label_list, public_status):
        tags = obj.tags
        for label in tag_label_list:
            tags.append(self.get_or_create_tag(label, public_status))
