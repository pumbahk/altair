from altaircms.solr import api as solrapi

def pageset_id_list_from_words(request, words, query_cond):
    fulltext_search = solrapi.get_fulltext_search(request)
    solr_query = create_query_from_freeword(words, query_cond=query_cond)
    result = fulltext_search.search(solr_query, fields=["pageset_id"])
    
    return [f["pageset_id"] for f in result]

def _create_dict_from_word(word):
    """ 検索用の辞書作る
    solrに格納される各フィールドはcopyfieldとしてsearchtextが設定されている。
    (see: buildout.cfg 'solr' section)
    """
    return dict(searchtext=word)
    
def create_query_from_freeword(words, query_cond=None):
    assert query_cond in ("intersection", "union")
    
    if query_cond == "intersection":
        cop = u" AND "
    elif query_cond == "union":
        cop = u" OR "

    q = solrapi.SolrSearchQuery(_create_dict_from_word(words[0]))
    for word in words[1:]:
        q = q.compose(solrapi.SolrSearchQuery(_create_dict_from_word(word)), cop)
    return q
