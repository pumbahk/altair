# -*- coding:utf-8 -*-

from altaircms.solr import api
from altaircms.page.models import Page
import sys
# import logging
# logger = logging.getLogger()
# logger.setLevel(logging.DEBUG)

if len(sys.argv) > 1:
    page_id = sys.argv[1] 
else:
    page_id = 1


from pyramid import testing
config = testing.setUp(
    settings={"altaircms.solr.server.url": "http://localhost:8080/solr"})
request = testing.DummyRequest(
    registry=config.registry)

from altaircms.solr import directives
directives.add_fulltext_search(config, "altaircms.solr.api.SolrSearch")

###
page = Page(id=page_id, title=u"title", description=u"何かテキトーに")
doc = api.create_doc_from_page(page)

print "--- register ---"
ftsearch = api.get_fulltext_search(request)
print ftsearch.register(doc, commit=True)


print "--- search ---"
query =  api.create_query_from_dict(
    page_title=u"title", 
    page_description=u"何か"
    )
print "query: %s" % query
print "-------------"
print ftsearch.search(query).results

print ftsearch.search(api.create_query_from_dict(id=1)).results
print ftsearch.search(api.create_query_from_dict(page_description=u"何かテキトーに")).results
