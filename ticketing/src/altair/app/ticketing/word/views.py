# -*- coding:utf-8 -*-
import webhelpers.paginate as paginate
from altair.app.ticketing.core.utils import PageURL_WebOb_Ex
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.views import BaseView
from altair.pyramid_dynamic_renderer import lbr_view_config
from pyramid.view import view_defaults


@view_defaults(decorator=with_bootstrap,
               permission="event_editor")
class WordView(BaseView):
    def __init__(self, context, request):
        super(WordView, self).__init__(context, request)

    @lbr_view_config(route_name='word.index',
                     renderer='altair.app.ticketing:templates/word/index.html')
    def index(self):
        words = paginate.Page(
            self.context.get_words(),
            page=int(self.request.params.get('page', 0)),
            items_per_page=50,
            url=PageURL_WebOb_Ex(self.request)
        )
        return {
            'words': words
        }
