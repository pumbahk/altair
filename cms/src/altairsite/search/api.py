# -*- encoding:utf-8 -*-

from altaircms.solr import api as solrapi

def pageset_id_list_from_words(request, words, query_cond):
    assert query_cond in ("intersection", "union")

    fulltext_search = solrapi.get_fulltext_search(request)
    solr_query = solrapi.create_query_from_freewords(words, query_cond=query_cond)
    result = fulltext_search.search(solr_query, fields=["pageset_id"])
    
    return [f["pageset_id"] for f in result]

def search_by_freeword(request, freeword, query_cond="intersection"): #query_cond = {union, intersection}
    """ freeword検索した結果を返す(pageset のquery)"""
    from . import searcher
    query_params = dict(query=freeword, query_cond="intersection")
    qs = searcher.get_pageset_query_from_freeword(request, query_params)
    return qs
