from pyramid.view import view_config
from . import api

@view_config(route_name="solr_search", renderer="json")
def solr_search_view(request):
    params = request.GET
    query = api.create_query_from_dict(params)
    ftsearch = api.get_fulltext_search(request)
    result = ftsearch.search(query)
    return result
    
