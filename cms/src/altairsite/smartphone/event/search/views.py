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
    return {
        'helper':helper
    }
