# -*- coding:utf-8 -*-
import webhelpers.paginate as paginate
from altair.app.ticketing.api.impl import get_communication_api
from altair.app.ticketing.core.utils import PageURL_WebOb_Ex
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.users.models import WordSubscription
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
    @lbr_view_config(route_name='word.sync', request_method="GET",
                     renderer='altair.app.ticketing:templates/word/index.html')
    @lbr_view_config(route_name='word.download', request_method="GET",
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

    @lbr_view_config(route_name='word.download', request_method="POST",
                     renderer='word_csv')
    def word_download(self):
        header = [
            u'word_id'
            , u'label'
            , u'authz_identifier'
            , u'email_1'
            , u'sex'
            , u'birthday'
            , u'prefecture'
        ]
        word_id = self.request.matchdict["word_id"]
        subscriptions = WordSubscription.query.filter(WordSubscription.word_id == word_id).all()

        rows = []
        for subscription in subscriptions:
            if not subscription.word or not subscription.user or not subscription.user.user_credential \
                    or not subscription.user.shipping_addresses:
                continue
            sex = subscription.user.shipping_addresses[0].sex
            sex_status = u"不明"
            if sex == 1:
                sex_status = u"男"
            if sex == 2:
                sex_status = u"女"

            birthday = subscription.user.shipping_addresses[0].birthday.strftime("%Y/%m/%d") if \
            subscription.user.shipping_addresses[0].birthday else u"不明"
            row = [
                unicode(subscription.word_id),
                subscription.word.label,
                subscription.user.user_credential[0].authz_identifier,
                subscription.user.shipping_addresses[0].email_1,
                sex_status,
                unicode(birthday),
                subscription.user.shipping_addresses[0].prefecture,
            ]
            rows.append(row)
        return {'header': header, 'rows': rows}
