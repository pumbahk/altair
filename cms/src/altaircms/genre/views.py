# -*- coding:utf-8 -*-

import logging
logger  = logging.getLogger(__name__)

from pyramid.view import view_config
from altaircms.models import Genre

from .searcher import GenreSearcher

def build_genre_dict(genre):
    return {"label": genre.label, "pk": genre.id}

@view_config(renderer="json", route_name="api_genre_children", request_param="genre_id")
def genre_children(context, request):
    try:
        searcher = GenreSearcher(request)
        genre = request.allowable(Genre).filter_by(id=request.GET["genre_id"])
        children = searcher.get_children(genre)
        data = [build_genre_dict(g) for g in children]
        return {"status": True, "data": data}
    except Exception, e:
        logger.exception(str(e))
        return {"status": False, "message": u"ジャンルが見つかりません"}

## TODO: combobox
