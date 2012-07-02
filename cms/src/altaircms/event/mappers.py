# coding: utf-8
from ..slackoff.mappers import model_to_dict
from ..slackoff.mappers import ObjectLike

def event_mapper(request, obj):
    objlike = ObjectLike(**model_to_dict(obj))
    return objlike
