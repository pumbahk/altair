from altaircms.solr import api as solr
from zope.interface import implementer
from altaircms.interfaces import IModelEvent

def notify_page_create(request, page, params=None):
    registry = request.registry
    return registry.notify(PageCreate(request, page, params))

def notify_page_update(request, page, params=None):
    registry = request.registry
    return registry.notify(PageUpdate(request, page, params))

def notify_page_delete(request, page, params=None):
    registry = request.registry
    return registry.notify(PageDelete(request, page, params))

@implementer(IModelEvent)
class PageCreate(object):
    def __init__(self, request, obj, params=None):
        self.request = request
        self.obj = obj
        self.params = params

@implementer(IModelEvent)
class PageUpdate(object):
    def __init__(self, request, obj, params=None):
        self.request = request
        self.obj = obj
        self.params = params


@implementer(IModelEvent)
class PageDelete(object):
    def __init__(self, request, obj, params=None):
        self.request = request
        self.obj = obj
        self.params = params

def page_register_solr(self):
    page = self.obj
    ftsearch = solr.get_fulltext_search(self.request)
    doc = solr.create_doc_from_page(page)
    ftsearch.register(doc, commit=True)
 
def page_delete_solr(self):
    page = self.obj
    ftsearch = solr.get_fulltext_seayrch(self.request)
    doc = solr.create_doc_from_dict({"page_id": page.id})
    ftsearch.delete(doc, commit=True)
