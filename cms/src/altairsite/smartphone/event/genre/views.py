# -*- coding:utf-8 -*-
from altairsite.config import usersite_view_config

@usersite_view_config(route_name='genre',request_type="altairsite.tweens.ISmartphoneRequest"
             , renderer='altairsite.smartphone:templates/genre/genre.html')
def moveGenre(context, request):

    return context.get_genre_render_param()