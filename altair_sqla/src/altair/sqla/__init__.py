import itertools

def association_proxy_many(target_name, attr_name):
    return AssociationProxyMany(target_name, attr_name)

class AssociationProxyMany(object):
    def __init__(self, target_name, attr_name, collection_type=list):
        self.target_name = target_name
        self.attr_name = attr_name
        self.collection_type = collection_type


    def __get__(self, obj, class_):
        target = getattr(obj, self.target_name)
        return self.collection_type(itertools.chain(*[getattr(t, self.attr_name)
                                                      for t in target]))
