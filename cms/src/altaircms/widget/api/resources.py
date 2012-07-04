# -*- coding:utf-8 -*-
from altaircms.models import DBSession
from altaircms.security import RootFactory

def set_with_dict(obj, D):
    for k, v in D.items():
        setattr(obj, k, v)
    return obj

class WidgetResource(RootFactory):
    def add(self, data, flush=False):
        DBSession.add(data)
        if flush:
            DBSession.flush()
        
    def delete(self, data, flush=False):
        DBSession.delete(data)
        if flush:
            DBSession.flush()
