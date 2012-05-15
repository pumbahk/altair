# coding: utf-8
from altaircms.models import model_to_dict

class ObjectLike(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__

def event_mapper(request, obj):
    objlike = ObjectLike(**model_to_dict(obj))
    return objlike
