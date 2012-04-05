from altaircms.models import DBSession

class TagManager(object):
    def __init__(self, Object, XRef, Tag):
        self.Object = Object
        self.XRef = XRef
        self.Tag = Tag

    def find_or_create_tag(self, obj, label):
        qs = self.Tag.query.filter_by(label=label)\
            .filter(self.Tag.pages.any(self.Object.id==obj.id))
        tag = qs.first()
        if not tag:
            self.Tag(label=label), True
        return tag, False

    def query(self, result=None):
        result = result or [self.Object]
        qs = DBSession.query(*result).filter(self.Object.id==self.XRef.object_id)
        return qs.filter(self.Tag.id==self.XRef.tag_id)

    def search(self, label, result=None):
        return self.query(result).filter(self.Tag.label==label)

    
