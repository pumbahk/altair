# -*- coding:utf-8 -*-
from altairsite.config import usersite_view_config

from pyramid.renderers import render_to_response

@usersite_view_config(route_name='smartphone.genre',request_type="altairsite.tweens.ISmartphoneRequest"
             , renderer='altairsite.smartphone:templates/genre/genre.html')
def move_genre(context, request):

    genre_id = request.matchdict.get('genre_id')
    if context.is_sub_sub_genre(genre_id=genre_id):
        render_param = context.get_subsubgenre_render_param(genre_id=genre_id)
        return render_to_response('altairsite.smartphone:templates/searchresult/subgenre.html', render_param, request=request)

    return context.get_genre_render_param(None)
