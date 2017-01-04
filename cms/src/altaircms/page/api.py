# -*- encoding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)

from altaircms.solr import api as solr
from altaircms.modelmanager.searcher import IPublishingModelSearcher
from altaircms.page.models import PageSet
from . import StaticPageNotFound
from .staticupload.api import get_static_page_utility
from .staticupload.api import set_static_page_utility
from .staticupload.api import as_static_page_response

def get_pageset_searcher(request):
    return request.registry.queryUtility(IPublishingModelSearcher, name="page")(request)


### solr
def doc_from_tags(doc, tags):
    vs = [tag.label for tag in tags]
    doc.update(page_tag=vs)
    return doc 

def doc_from_performances(doc, performances):
    vs = [p.venue for p in performances]
    doc.update(performance_venue=vs)
    return doc

def _split_text(text):
    if text is None:
        return []
    tags = [e.strip() for e in text.split(",")] ##
    return [k for k in tags if k]

def doc_from_event(doc, event): ## fixme
    doc.update(event_title=event.title, 
               event_subtitle=event.subtitle, 
               event_performer=_split_text(event.performers), 
               event_description=event.description)
    return doc 

def _doc_from_page(doc, page):
    doc.update(page_description=page.description, 
               page_title=page.title, 
               page_id=page.id,
               page_keywords=page.keywords)
    if page.pageset:
        doc.update(id=page.pageset.id, 
                   pageset_id=page.pageset.id)
        tags = page.pageset.public_tags
        if tags:
            doc = doc_from_tags(doc, tags)
    return doc
    
def doc_from_page(page):
    """ id == page.pageset.id 
    """
    doc = solr.SolrSearchDoc()
    event = page.event or (page.pageset.event if page.pageset else None) #for safe
    if event:
        doc = doc_from_event(doc, event)
        doc = doc_from_performances(doc, event.performances)
        
    _doc_from_page(doc, page)
    return doc

def ftsearch_register_from_page(request, page, ftsearch=None):
    ftsearch = ftsearch or solr.get_fulltext_search(request)
    doc = doc_from_page(page)
    try:
        ftsearch.register(doc, commit=True)
    except Exception, e:
        logger.warn(str(e))
        

def ftsearch_delete_register_from_page(request, page, ftsearch=None):
    ftsearch = ftsearch or solr.get_fulltext_search(request)
    doc = solr.create_doc_from_dict({"page_id": page.id})
    try:
        ftsearch.delete(doc, commit=True)
    except Exception, e:
        logger.error("solr delete failed")
        logger.exception(str(e))


def get_pageset_from_event_id(request, event_id):
    return request.allowable(PageSet).filter(PageSet.event_id==event_id).first()