# -*- coding:utf-8 -*-
import webhelpers.paginate as paginate
from altair.app.ticketing.api.impl import get_communication_api
from altair.app.ticketing.core.utils import PageURL_WebOb_Ex
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.views import BaseView
from altair.pyramid_dynamic_renderer import lbr_view_config
from pyramid.view import view_defaults

from .api import CMSWordsApi
from .forms import SearchForm


@view_defaults(decorator=with_bootstrap,
               permission="event_editor")
class WordView(BaseView):
    def __init__(self, context, request):
        super(WordView, self).__init__(context, request)

    @lbr_view_config(route_name='word.index',
                     renderer='altair.app.ticketing:templates/word/index.html')
    def index(self):
        search_form = SearchForm(self.request.GET)
        words = paginate.Page(
            self.context.get_words(search_form),
            page=int(self.request.params.get('page', 0)),
            items_per_page=50,
            url=PageURL_WebOb_Ex(self.request)
        )
        return {
            'search_form': search_form,
            'words': words
        }

    @lbr_view_config(route_name='word.sync', request_method="POST",
                     renderer='altair.app.ticketing:templates/word/index.html')
    def sync(self):
        communication_api = get_communication_api(self.request, CMSWordsApi)
        response = communication_api.create_response("/api/word/getter")
        self.context.save_words(response)

        words = paginate.Page(
            self.context.get_words(),
            page=int(self.request.params.get('page', 0)),
            items_per_page=50,
            url=PageURL_WebOb_Ex(self.request)
        )
        return {
            'search_form': SearchForm(),
            'words': words
        }
