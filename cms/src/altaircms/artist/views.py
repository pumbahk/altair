# -*- coding:utf-8 -*-
from ..lib.fanstatic_decorator import with_bootstrap
from pyramid.view import notfound_view_config, view_config, forbidden_view_config, view_defaults


@view_defaults(decorator=with_bootstrap)
class ArtistView(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(route_name="artist_list", request_method="GET",
                 renderer="altaircms:templates/artist/list.html", permission="artist_read")
    def artist_list_get(self):

        return {}
