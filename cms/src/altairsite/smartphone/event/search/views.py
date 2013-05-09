# -*- coding:utf-8 -*-
from altairsite.config import usersite_view_config
from altairsite.smartphone.common.helper import SmartPhoneHelper
from altairsite.smartphone.event.search.forms import SearchForm

@usersite_view_config(route_name='search',request_type="altairsite.tweens.ISmartphoneRequest"
             , renderer='altairsite.smartphone:templates/searchresult/result.html')
def moveSearch(context, request):

    form = SearchForm(request.GET)
    helper = SmartPhoneHelper()
    qs = context.search_freeword(form.data['word'])
    result = context.create_result(qs=qs, page=int(form.data['page']), query=form.data['word'], per=10)
    return {
         'result':result
        ,'helper':helper
    }
