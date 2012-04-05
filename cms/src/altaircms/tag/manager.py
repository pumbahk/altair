from altaircms.models import DBSession

class TagManager(object):
    def __init__(self, Object, XRef, Tag):
        self.Object = Object
        self.XRef = XRef
        self.Tag = Tag

    def maybe(self, label):
        tag = self.Tag.query.filter_by(label=label).first()
        if not tag:
            return self.Tag(label=label)
        else:
            return tag

    def query(self, result=None):
        result = result or [self.Object]
        qs = DBSession.query(*result).filter(self.Object.id==self.XRef.object_id)
        return qs.filter(self.Tag.id==self.XRef.tag_id)

    def search(self, label, result=None):
        """
        search matched objects
        """
        return self.query(result).filter(self.Tag.label==label)

    def delete(self, obj, deletes):
        """ deletes: [string]
        """
        tags = obj.tags
        qs = self.Tag.query.filter(self.XRef.object_id==obj.id)
        for tag in qs.filter(self.Tag.label.in_(deletes)):
            tags.remove(tag)
        
    def replace(self, obj, tag_label_list):
        if obj.tags:
            return self.fullreplace(obj, tag_label_list)
        else:
            return self.add_tags(obj, tag_label_list)

    def fullreplace(self, obj, tag_label_list):
        prev_name_set = set(x.label for x in obj.tags)
        deletes = prev_name_set.difference(tag_label_list)
        self.delete(obj, deletes)
        updates = set(tag_label_list).difference(prev_name_set)

        for label in updates:
             obj.tags.append(self.maybe(label))

    def add_tags(self, obj, tag_label_list):
        tags = obj.tags
        for label in tag_label_list:
             tags.append(self.maybe(label))
        
        

    
