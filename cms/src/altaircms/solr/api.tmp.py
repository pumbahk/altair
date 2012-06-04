# -*- encoding:utf-8 -*-

from altaircms.solr.api import *

print SolrSearchQuery(dict(x="y", a="y")).query_string
print SolrSearchQuery(dict(x="y", a="y")).NOT().query_string
print SolrSearchQuery(dict(page_title=u"ブルー", page_description=u"ブルー")).AND(SolrSearchQuery(dict(page_title=u"blueman", page_description=u"blueman"))).query_string

print SolrSearchQuery(dict(page_title=u"ブルー", page_description=u"ブルー")).NOT().AND(SolrSearchQuery(dict(page_title=u"blueman", page_description=u"blueman"))).query_string

print NullSearchQuery().OR(dict(x="y")).query_string

print u"========================================"

print create_query_from_freeword([u"abc"], "union").query_string

print u"----------------------------------------"
print create_query_from_freeword([u"abc", u"xyz"], "intersection").query_string

import solr
s = solr.Solr("http://localhost:8080/solr")
print create_query_from_freeword([u"ブルー"], "union").query_string
print s.select(create_query_from_freeword([u"ブルー"], "union").query_string, fields=["id"]).results
