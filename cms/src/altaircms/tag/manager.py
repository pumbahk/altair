from altaircms.models import DBSession

class TagManager(object):
    def __init__(self, Object, XRef, Tag):
        self.Object = Object
        self.XRef = XRef
        self.Tag = Tag

    def maybe(self, label, public_status=True):
        tag = self.Tag.query.filter_by(label=label, publicp=public_status).first()
        if not tag:
            return self.Tag(label=label, publicp=public_status)
        else:
            return tag

    ## search
    def query(self, result=None):
        result = result or [self.Object]
        qs = DBSession.query(*result).filter(self.Object.id==self.XRef.object_id)
        return qs.filter(self.Tag.id==self.XRef.tag_id)

    def public_search(self, label, result=None):
        return self.search(label, result=result).filter(self.Tag.publicp==True)

    def unpublic_search(self, label, result=None):
        return self.search(label, result=result).filter(self.Tag.publicp==False)

    def search(self, label, result=None):
        """
        search matched objects
        """
        return self.query(result).filter(self.Tag.label==label)

    ## alter
    def delete(self, obj, deletes, public_status=True):
        """ deletes: [unicode]
        """
        if deletes:
            tags = obj.tags
            qs = self.Tag.query.filter(self.XRef.object_id==obj.id).filter(self.Tag.publicp == public_status)
            for tag in qs.filter(self.Tag.label.in_(deletes)):
                tags.remove(tag)
        
    def replace(self, obj, tag_label_list, public_status=True):
        if obj.tags:
            return self.fullreplace(obj, tag_label_list, public_status)
        else:
            return self.add_tags(obj, tag_label_list, public_status)

    def fullreplace(self, obj, tag_label_list, public_status):
        prev_name_set = set(x.label for x in obj.tags if x.publicp == public_status)
        deletes = prev_name_set.difference(tag_label_list)
        self.delete(obj, deletes)
        updates = set(tag_label_list).difference(prev_name_set)

        for label in updates:
            obj.tags.append(self.maybe(label, public_status))

    def add_tags(self, obj, tag_label_list, public_status):
        tags = obj.tags
        for label in tag_label_list:
            tags.append(self.maybe(label, public_status))
        
        

    
