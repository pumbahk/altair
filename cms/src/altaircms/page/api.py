# -*- encoding:utf-8 -*-

from altaircms.solr import api as solr

def doc_from_tags(doc, tags):
    vs = [tag.label for tag in tags]
    doc.update(page_tag=vs)
    return doc 

def doc_from_performances(doc, performances):
    vs = [p.venue for p in performances]
    import warnings
    warnings.warn("need update solr environment, but not a good opotunity, now, so disable it.")
    # doc.update(performance_venue=vs)
    return doc

def doc_from_event(doc, event): ## fixme
    doc.update(event_title=event.title, 
               event_subtitle=event.subtitle, 
               event_place=event.place, 
               event_description=event.description)
    return doc 

def _doc_from_page(doc, page):
    doc.update(page_description=page.description, 
               page_title=page.title, 
               page_id=page.id)
    if page.pageset:
        doc.update(id=page.pageset.id, 
                   pageset_id=page.pageset.id)
    return doc
    
def doc_from_page(page):
    """ id == page.pageset.id 
    """
    doc = solr.SolrSearchDoc()
    event = page.event or (page.pageset.event if page.pageset else None) #for safe
    if event:
        doc = doc_from_event(doc, event)
        doc = doc_from_performances(doc, event.performances)

    tags = page.public_tags
    if tags:
        doc = doc_from_tags(doc, tags)
        
    _doc_from_page(doc, page)
    return doc


def ftsearch_register_from_page(request, page, ftsearch=None):
    ftsearch = ftsearch or solr.get_fulltext_search(request)
    doc = doc_from_page(page)
    ftsearch.register(doc, commit=True)


def ftsearch_delete_register_from_page(request, page, ftsearch=None):
    ftsearch = ftsearch or solr.get_fulltext_search(request)
    doc = solr.create_doc_from_dict({"page_id": page.id})
    ftsearch.delete(doc, commit=True)
