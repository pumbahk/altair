import solr
import logging
logger = logging.getLogger(__name__)
from zope.interface import implementer
from pyramid.decorator import reify
from .interfaces import IFulltextSearch


def get_fulltext_search(request):
    search_cls = request.registry.getUtility(IFulltextSearch)
    return search_cls.create_from_request(request)

class SolrSearchQuery(object):
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def __repr__(self):
        return str(self.kwargs)

    @reify
    def query_string(self):
        kwargs = self.kwargs
        return ", ".join(u"%s:%s" % (k, v) for k, v in kwargs.iteritems())

class SolrSearchDoc(object):
    def __init__(self, doc=None):
        self.doc = doc or {}
    
    def __repr__(self):
        return str(self.doc)

    def update(self, D):
        self.doc.update(D)

    @reify
    def query_doc(self):
        return self.doc

## query
def create_query_from_dict(D__=None, **kwargs):
    return SolrSearchQuery(D__ or kwargs)

def create_query_from_freeword(word):
    return dict(event_title=word, 
                event_subtitle=word, 
                event_place=word, 
                page_description=word, 
                page_title=word, 
                page_keywords=word, 
                )

## doc
def create_doc_from_dict(D):
    return SolrSearchDoc(D)
                
def create_doc_from_event(event): ## fixme
    return SolrSearchDoc(
        dict(event_title=event.title, 
             event_subtitle=event.subtitle, 
             event_place=event.place
             ))

def create_doc_from_page(page):
    """ id == page.pageset.id 
    """
    if page.event:
        doc = create_doc_from_event(page.event)
    else:
        doc = SolrSearchDoc()

    doc.update(
        dict(page_description=page.description, 
             page_title=page.title, 
             page_keywords=page.keywords, 
             id=page.pageset.id, 
             page_id=page.id))
    return doc

@implementer(IFulltextSearch)
class SolrSearch(object):
    """ fulltext search via solr
    """
    SETTINGS_KEY_NAME = "altaircms.solr.server.url"

    @classmethod
    def create_from_request(cls, request):
        settings = request.registry.settings
        return cls(settings[cls.SETTINGS_KEY_NAME])

    def __init__(self, server_url):
        self.server_url = server_url

    @reify
    def solr(self):
        return solr.Solr(self.server_url)

    def commit(self):
        return self.solr.commit()

    def search(self, query):
        logger.debug(u"fulltext search query: %s" % query)
        return self.solr.select(query.query_string).results

    def register(self, doc, commit=False):
        logger.debug(u"fulltext search register: %s" % doc)
        self.solr.add(doc.query_doc, commit=commit)

    def delete(self, doc, commit=False):
        logger.debug(u"fulltext search delete: %s" % doc)
        self.solr.delete(doc.query_doc)
        if commit:
            self.solr.commit()

@implementer(IFulltextSearch)
class DummySearch(object):
    @classmethod
    def create_from_request(cls, request):
        return cls()

    def search(self, query):
        logger.info(u"fulltext search query: %s" % query)
        return []

    def register(self, doc, *args, **kwargs):
        logger.info(u"fulltext search register: %s" % doc)

    def delete(self, doc, *args, **kwargs):
        logger.info(u"fulltext search delete: %s" % doc)
