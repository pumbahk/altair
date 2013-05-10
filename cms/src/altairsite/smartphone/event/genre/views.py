# -*- coding:utf-8 -*-
from altairsite.config import usersite_view_config
from altairsite.smartphone.common.helper import SmartPhoneHelper
from altairsite.smartphone.event.search.forms import GenreSearchForm

@usersite_view_config(route_name='genre',request_type="altairsite.tweens.ISmartphoneRequest"
             , renderer='altairsite.smartphone:templates/genre/genre.html')
def moveGenre(context, request):
    form = GenreSearchForm()
    genre_id = request.matchdict.get('genre_id')
    form.genre_id.data = genre_id
    genre = context.get_genre(id=genre_id)
    promotions = context.getInfo(kind="promotion", system_tag_id=genre_id)[0:5]
    topcontents = context.getInfo(kind="topcontent", system_tag_id=genre_id)[0:5]
    topics = context.getInfo(kind="topic", system_tag_id=genre_id)[0:5]
    hotwords = context.get_hotword()[0:5]
    genretree = context.get_genre_tree(parent=genre)
    areas = context.get_area()
    week_sales = context.search_week(genre.label, 1, 10)
    near_end_sales = context.search_week(genre.label, 1, 10)

    return {
         'genre':genre
        ,'promotions':promotions
        ,'topcontents':topcontents
        ,'topics':topics
        ,'hotwords':hotwords
        ,'genretree':genretree
        ,'areas':areas
        ,'week_sales':week_sales
        ,'near_end_sales':near_end_sales
        ,'helper':SmartPhoneHelper()
        ,'form':form
    }
