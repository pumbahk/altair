from altaircms.solr import api as solr
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
