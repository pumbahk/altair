# -*- coding:utf-8 -*-

"""
solrに必要なのはアクセス用のURL.::

  altaircms.solr.server_url = http://localhost:8080/solr
  altaircms.solr.search.utility = altaircms.solr.api.DummySearch or\
  altaircms.solr.search.utility = altaircms.solr.api.SolrSearch
全文検索の機能の利用方法::

  ftsearch = api.get_fulltext_search(request)

  ## query
  ftsearch.search(query)

  ## register
  ftsearch.register(args)
"""

def includeme(config):
    config.add_directive("add_fulltext_search", ".directives.add_fulltext_search")

    ## debug
    import warnings
    warnings.warn("debug view added /solr")
    config.scan(".")
    config.add_route("solr_search", "/solr") #debug

