# coding: utf-8
from altaircms.models import DBSession
from altaircms.auth.models import Permission

def groupfinder(userid, request):
    objects = DBSession.query(Permission).filter_by(operator_id=userid)
    perms = []

    for obj in objects:
        perms.append(obj.permission)

    return perms
