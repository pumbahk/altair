from altaircms.solr import api as solrapi

def pageset_id_list_from_words(request, words, query_cond):
    fulltext_search = solrapi.get_fulltext_search(request)
    solr_query = solrapi.create_query_from_freeword(words, query_cond=query_cond)
    result = fulltext_search.search(solr_query, fields=["pageset_id"])
    
    return [f["pageset_id"] for f in result]

