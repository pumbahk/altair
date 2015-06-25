# encoding: utf-8
import logging
from datetime import datetime
from pyramid.view import view_defaults, view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember, forget
from altair.sqlahelper import get_db_session
from altair.app.ticketing.famiport.models import FamiPortPerformance, FamiPortEvent
from .api import lookup_user_by_credentials, lookup_performance_by_searchform_data
from .forms import (
    LoginForm,
    SearchPerformanceForm,
)
from webhelpers import paginate
from altair.app.ticketing.core.utils import PageURL_WebOb_Ex
from .helpers import ViewHelpers

logger = logging.getLogger(__name__)

class FamiPortOpToolTopView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(route_name='top', renderer='top.mako', permission='operator')
    def top(self):
        return dict()


class FamiPortOpLoginView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(route_name='login', renderer='login.mako')
    def get(self):
        return_url = self.request.params.get('return_url', '')
        return dict(form=LoginForm(), return_url=return_url)
        
    @view_config(route_name='login', request_method='POST', renderer='login.mako')
    def post(self):
        return_url = self.request.params.get('return_url')
        if not return_url:
            return_url = self.request.route_path('top')
        form = LoginForm(formdata=self.request.POST)
        if not form.validate():
            return dict(form=form, return_url=return_url)
        user = lookup_user_by_credentials(
            self.request,
            form.user_name.data,
            form.password.data
            )
        if user is None:
            self.request.session.flash(u'ユーザ名とパスワードの組み合わせが誤っています')
            return dict(form=form, return_url=return_url)

        remember(self.request, user.id)
        return HTTPFound(return_url)

class FamiPortOpLogoutView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(route_name='logout', renderer='logout.mako')
    def get(self):
        forget(self.request)
        return HTTPFound(self.request.route_path('login'))

class FamiPortOpToolExampleView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(route_name='example.page_needs_authentication', renderer='example/page_needs_authentication.mako', permission='operator')
    def page_needs_authentication(self):
        return dict()

class FamiPortSearchView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    # @view_config(route_name='index', renderer='altair.app.ticketing.famiport.optool:templates/order_search.html', permission='operator')
    @view_config(route_name='search.order', renderer='altair.app.ticketing.famiport.optool:templates/order_search.mako', permission='operator')
    def search_order(self):
        # TODO Search order
        return dict()

    @view_config(route_name='search.performance', renderer='altair.app.ticketing.famiport.optool:templates/performance_search.mako', permission='operator')
    def search_performance(self):
        form = SearchPerformanceForm()

        if self.request.POST or self.request.params:
            postdata = self.request.POST
            form = SearchPerformanceForm(postdata)
            if form.validate():
                performances = lookup_performance_by_searchform_data(self.request, postdata)
                count = len(performances)
                page_url = PageURL_WebOb_Ex(self.request)
                pages = paginate.Page(performances,
                                     page=self.request.GET.get('page', '1'),
                                     item_count=count,
                                     items_per_page=20,
                                     url=page_url)
            else:
                if not postdata.get('event_code_1') and postdata.get('event_code_2'):
                    self.request.session.flash(u'mainとsubセットでご入力下さい')
                return dict(form=form,count=None,entries=[])
        else:
            count = None
            pages = []

        return dict(form=form,
                    count=count,
                    entries=pages)

    @view_config(route_name='search.refund_performance', renderer='altair.app.ticketing.famiport.optool:templates/refund_performance_search.mako', permission='operator')
    def search_refund_performance(self):
        # TODO Search refund performance
        return dict()

    @view_config(route_name='search.refund_ticket', renderer='altair.app.ticketing.famiport.optool:templates/refund_ticket_search.mako', permission='operator')
    def search_refund_performance(self):
        # TODO Search refund ticket
        return dict()

# TODO Make sure the permission of each operation
class FamiPortDetailView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request


    @view_config(route_name='order.detail', renderer='altair.app.ticketing.famiport.optool:templates/order_detail.mako')
    def show_order_detail(self):
        # TODO Show order detail
        return dict()

    @view_config(route_name='performance.detail', renderer='altair.app.ticketing.famiport.optool:templates/performance_detail.mako', permission='operator')
    def show_performance_detail(self):
        performance = self.context.performance
        return dict(performance=performance, h=ViewHelpers(),)

    # TODO refund_performance.htmlはperformance_detail.htmlと統合できそう
    @view_config(route_name='refund_performance.detail', renderer='altair.app.ticketing.famiport.optool:templates/refund_performance_detail.mako')
    def show_refund_performance_detail(self):
        # TODO Show performance detail
        return dict()

# TODO Make sure the permission of each operation
class FamiPortRebookOrderView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(route_name='rebook_order', request_method='GET', renderer='altair.app.ticketing.famiport.optool:templates/rebook_order.mako', permission='operator')
    def rebook_order(self):
        # TODO rebook order
        return dict()

    @view_config(route_name='rebook_order', request_method='POST', match_param='action=rebook', renderer='altair.app.ticketing.famiport.optool:templates/rebook_order.mako', permission='operator')
    def rebook_order(self):
        # TODO rebook order
        return dict()

    @view_config(route_name='rebook_order', request_method='POST', match_param='action=reprint', renderer='altair.app.ticketing.famiport.optool:templates/rebook_order.mako', permission='operator')
    def reprint_ticket(self):
        # TODO reprint order
        return dict()