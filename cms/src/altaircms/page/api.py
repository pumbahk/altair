# -*- encoding:utf-8 -*-

from altaircms.solr import api as solr

def create_doc_from_event(event): ## fixme
    return solr.SolrSearchDoc(
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
        doc = solr.SolrSearchDoc()

    doc.update(
        dict(page_description=page.description, 
             page_title=page.title, 
             page_keywords=page.keywords, 
             id=page.pageset.id, 
             page_id=page.id))
    return doc


def ftsearch_register_from_page(request, page):
    ftsearch = solr.get_fulltext_search(request)
    doc = create_doc_from_page(page)
    ftsearch.register(doc, commit=True)


def ftsearch_delete_register_from_page(request, page):
    ftsearch = solr.get_fulltext_search(request)
    doc = solr.create_doc_from_dict({"page_id": page.id})
    ftsearch.delete(doc, commit=True)
