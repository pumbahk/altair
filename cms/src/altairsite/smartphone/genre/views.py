# -*- coding:utf-8 -*-
from altairsite.config import smartphone_site_view_config
from altairsite.separation import selectable_renderer
from pyramid.renderers import render_to_response
from pyramid.httpexceptions import HTTPFound

@smartphone_site_view_config(route_name='smartphone.genre',request_type="altairsite.tweens.ISmartphoneRequest"
             , renderer=selectable_renderer('altairsite.smartphone:templates/genre/genre.html'))
def move_genre(context, request):

    genre_id = request.matchdict.get('genre_id')
    genre = context.get_genre(genre_id)
    if not genre:
        return HTTPFound(request.route_path('smartphone.main'))

    if context.is_sub_sub_genre(genre_id=genre_id):
        render_param = context.get_subsubgenre_render_param(genre_id=genre_id)
        return render_to_response(selectable_renderer('altairsite.smartphone:templates/searchresult/subgenre.html'), render_param, request=request)

    return context.get_genre_render_param(None)
