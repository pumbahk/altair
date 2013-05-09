# -*- coding:utf-8 -*-
from altairsite.config import usersite_view_config
from altairsite.smartphone.common.helper import SmartPhoneHelper
from altairsite.smartphone.event.search.forms import SearchForm

@usersite_view_config(route_name='genre',request_type="altairsite.tweens.ISmartphoneRequest"
             , renderer='altairsite.smartphone:templates/genre/genre.html')
def moveGenre(context, request):
    genre_id = request.matchdict.get('genre_id')
    genre = context.get_genre(id=genre_id)
    promotions = context.search(kind="promotion", system_tag_id=genre_id)[0:5]
    topcontents = context.search(kind="topcontent", system_tag_id=genre_id)[0:5]
    topics = context.search(kind="topic", system_tag_id=genre_id)[0:5]
    hotwords = context.get_hotword()[0:5]
    genretree = context.get_genre_tree(parent=genre)
    regions = context.get_region()
    helper = SmartPhoneHelper()

    return {
         'genre':genre
        ,'promotions':promotions
        ,'topcontents':topcontents
        ,'topics':topics
        ,'hotwords':hotwords
        ,'genretree':genretree
        ,'regions':regions
        ,'helper':helper
        ,'form':SearchForm()
    }
