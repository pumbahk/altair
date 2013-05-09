# -*- coding:utf-8 -*-
from altairsite.config import usersite_view_config
from altairsite.smartphone.common.helper import SmartPhoneHelper
from altairsite.smartphone.event.search.forms import SearchForm
from altairsite.smartphone.event.search.resources import SearchQuery

@usersite_view_config(route_name='search',request_type="altairsite.tweens.ISmartphoneRequest"
             , renderer='altairsite.smartphone:templates/searchresult/result.html')
def moveSearch(context, request):
    form = SearchForm(request.GET)
    helper = SmartPhoneHelper()
    query = SearchQuery(form.data['word'], form.data['sale'])
    qs = context.search_freeword(search_query=query)
    if qs:
        qs = context.search_sale(search_query=query, qs=qs)
    result = context.create_result(qs=qs, page=int(form.data['page']), query=query, per=10)

    return {
         'result':result
        ,'helper':helper
    }
