from altaircms.slackoff.mappers import ObjectLike
from altaircms.slackoff.mappers import model_to_dict

def freetext_body_mapper(request, obj):
    objlike = ObjectLike(**model_to_dict(obj))
    return objlike
