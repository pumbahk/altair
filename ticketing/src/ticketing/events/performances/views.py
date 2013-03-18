# -*- coding: utf-8 -*-

import re
import logging
logger = logging.getLogger(__name__)

import webhelpers.paginate as paginate
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.url import route_path
from pyramid.renderers import render_to_response
from pyramid.security import has_permission, ACLAllowed

from ticketing.models import merge_session_with_post, record_to_multidict
from ticketing.views import BaseView
from ticketing.fanstatic import with_bootstrap
from ticketing.events.performances.forms import PerformanceForm, PerformancePublicForm
from ticketing.core.models import Event, Performance, Order
from ticketing.products.forms import ProductForm, ProductItemForm
from ticketing.orders.forms import OrderForm, OrderSearchForm

from ticketing.mails.forms import MailInfoTemplate
from ticketing.models import DBSession
from ticketing.mails.api import get_mail_utility

from ticketing.core.models import MailTypeChoices

@view_defaults(decorator=with_bootstrap, permission="event_editor")
class PerformanceShowView(BaseView):
    def __init__(self, context, request):
        super(PerformanceShowView, self).__init__(context, request)
        # XXX: context でやったほうがいい?
        performance_id = int(self.request.matchdict.get('performance_id', 0))
        performance = Performance.query.filter(Performance.id == performance_id)\
                        .join(Event).filter(Event.organization_id == self.context.user.organization_id).first()
        if performance is None:
            raise HTTPNotFound('performance id %d is not found' % performance_id)
        self.performance = performance

    def _tab_seat_allocation(self):
        return {}

    def _tab_product(self):
        return dict(
            form_product=ProductForm(performance_id=self.performance.id),
            products=self.performance.products
            )

    def _tab_order(self):
        query = Order.filter_by(performance_id=self.performance.id)
        form_search = OrderSearchForm(
            self.request.params,
            event_id=self.performance.event_id,
            performance_id=self.performance.id)
        if form_search.validate():
            query = Order.set_search_condition(query, form_search)
        else:
            self.request.session.flash(u'検索条件が正しくありません')
        return dict(
            orders=paginate.Page(
                query,
                page=int(self.request.params.get('page', 0)),
                items_per_page=20,
                url=paginate.PageURL_WebOb(self.request)
                ),
            form_search=form_search,
            form_order=OrderForm(event_id=self.performance.event_id)
            )

    def _tab_sales_segment(self):
        return dict(sales_segments=self.performance.sales_segments)

    def _tab_reservation(self):
        return {}

    def _extra_data(self):
        # プリンターAPI
        return dict(
            endpoints=dict(
                (key, self.request.route_path('tickets.printer.api.%s' % key))
                for key in ['formats', 'peek', 'dequeue']
                )
            )

    @view_config(route_name='performances.show', renderer='ticketing:templates/performances/show.html', permission='event_viewer')
    @view_config(route_name='performances.show_tab', renderer='ticketing:templates/performances/show.html', permission='event_viewer')
    def show(self):
        tab = self.request.matchdict.get('tab', 'product')
        if not isinstance(has_permission('event_editor', self.request.context, self.request), ACLAllowed):
            if tab not in ['order', 'reservation']:
                tab = 'reservation'

        data = {
            'performance': self.performance,
            'tab': tab
            }

        tab_method = '_tab_' + tab.replace('-', '_')
        if not hasattr(self, tab_method):
            logger.warning("AttributeError: 'PerformanceShowView' object has no attribute '{0}'".format(tab_method))
            raise HTTPNotFound()
        data.update(getattr(self, tab_method)())
        data.update(self._extra_data())

        return data


@view_defaults(decorator=with_bootstrap, permission="event_editor")
class Performances(BaseView):

    @view_config(route_name='performances.index', renderer='ticketing:templates/performances/index.html', permission='event_viewer')
    def index(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id, organization_id=self.context.user.organization_id)
        if event is None:
            return HTTPNotFound('event id %d is not found' % event_id)

        sort = self.request.GET.get('sort', 'Performance.start_on')
        direction = self.request.GET.get('direction', 'asc')
        if direction not in ['asc', 'desc']:
            direction = 'asc'

        query = Performance.filter(Performance.event_id==event_id)
        query = query.order_by(sort + ' ' + direction)

        performances = paginate.Page(
            query,
            page=int(self.request.params.get('page', 0)),
            items_per_page=20,
            url=paginate.PageURL_WebOb(self.request)
        )

        return {
            'event':event,
            'performances':performances,
            'form':PerformanceForm(organization_id=self.context.user.organization_id),
        }


    @view_config(route_name='performances.new', request_method='GET', renderer='ticketing:templates/performances/edit.html')
    def new_get(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id, organization_id=self.context.user.organization_id)
        if event is None:
            return HTTPNotFound('event id %d is not found' % event_id)

        f = PerformanceForm(organization_id=self.context.user.organization_id)
        return {
            'form':f,
            'event':event,
        }

    @view_config(route_name='performances.new', request_method='POST', renderer='ticketing:templates/performances/edit.html')
    def new_post(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id, organization_id=self.context.user.organization_id)
        if event is None:
            return HTTPNotFound('event id %d is not found' % event_id)

        f = PerformanceForm(self.request.POST, organization_id=self.context.user.organization_id)
        if f.validate():
            performance = merge_session_with_post(Performance(), f.data)
            performance.event_id = event_id
            performance.create_venue_id = f.data['venue_id']
            performance.code = event.code + performance.code
            performance.save()

            self.request.session.flash(u'パフォーマンスを保存しました')
            return HTTPFound(location=route_path('performances.show', self.request, performance_id=performance.id))
        return {
            'form':f,
            'event':event,
        }

    @view_config(route_name='performances.edit', request_method='GET', renderer='ticketing:templates/performances/edit.html')
    @view_config(route_name='performances.copy', request_method='GET', renderer='ticketing:templates/performances/edit.html')
    def edit_get(self):
        performance_id = int(self.request.matchdict.get('performance_id', 0))
        performance = Performance.get(performance_id, self.context.user.organization_id)
        if performance is None:
            return HTTPNotFound('performance id %d is not found' % performance_id)

        is_copy = (self.request.matched_route.name == 'performances.copy')
        kwargs = dict(
            organization_id=self.context.user.organization_id,
            venue_id=performance.venue.id
        )

        f = PerformanceForm(**kwargs)
        f.process(record_to_multidict(performance))
        f.code.data = re.sub('^' + performance.event.code, '', f.code.data)

        if is_copy:
            f.original_id.data = f.id.data
            f.id.data = None

        return {
            'form':f,
            'event':performance.event,
        }

    @view_config(route_name='performances.edit', request_method='POST', renderer='ticketing:templates/performances/edit.html')
    @view_config(route_name='performances.copy', request_method='POST', renderer='ticketing:templates/performances/edit.html')
    def edit_post(self):
        performance_id = int(self.request.matchdict.get('performance_id', 0))
        performance = Performance.get(performance_id, self.context.user.organization_id)
        if performance is None:
            return HTTPNotFound('performance id %d is not found' % performance_id)

        is_copy = (self.request.matched_route.name == 'performances.copy')
        kwargs = dict(
            organization_id=self.context.user.organization_id,
            venue_id=performance.venue.id
        )

        f = PerformanceForm(self.request.POST, **kwargs)
        if f.validate():
            if is_copy:
                event_id = performance.event_id
                performance = merge_session_with_post(Performance(), f.data)
                performance.event_id = event_id
                performance.create_venue_id = f.data['venue_id']
            else:
                performance = merge_session_with_post(performance, f.data)
                if f.data['venue_id'] != performance.venue.id:
                    performance.delete_venue_id = performance.venue.id
                    performance.create_venue_id = f.data['venue_id']

            performance.code = performance.event.code + performance.code
            performance.save()
            self.request.session.flash(u'パフォーマンスを保存しました')
            return HTTPFound(location=route_path('performances.show', self.request, performance_id=performance.id))
        else:
            return {
                'form':f,
                'event':performance.event,
            }

    @view_config(route_name='performances.delete')
    def delete(self):
        performance_id = int(self.request.matchdict.get('performance_id', 0))
        performance = Performance.get(performance_id, self.context.user.organization_id)
        if performance is None:
            return HTTPNotFound('performance id %d is not found' % id)

        location = route_path('events.show', self.request, event_id=performance.event_id)
        try:
            performance.delete()
            self.request.session.flash(u'パフォーマンスを削除しました')
        except Exception, e:
            self.request.session.flash(e.message)
            raise HTTPFound(location=route_path('performances.show', self.request, performance_id=performance.id))

        return HTTPFound(location=location)

    @view_config(route_name='performances.open', request_method='GET',renderer='ticketing:templates/performances/_form_open.html')
    def open_get(self):
        performance_id = int(self.request.matchdict.get('performance_id', 0))
        performance = Performance.get(performance_id, self.context.user.organization_id)
        if performance is None:
            return HTTPNotFound('performance id %d is not found' % id)

        f = PerformancePublicForm(record_to_multidict(performance))
        f.public.data = 0 if f.public.data == 1 else 1
        return {
            'form':f,
            'performance':performance
        }

    @view_config(route_name='performances.open', request_method='POST',renderer='ticketing:templates/performances/_form_open.html')
    def open_post(self):
        performance_id = int(self.request.matchdict.get('performance_id', 0))
        performance = Performance.get(performance_id, self.context.user.organization_id)
        if performance is None:
            return HTTPNotFound('performance id %d is not found' % id)

        f = PerformancePublicForm(self.request.POST)
        if f.validate():
            performance = merge_session_with_post(performance, f.data)
            performance.save()

            if performance.public:
                self.request.session.flash(u'パフォーマンスを公開しました')
            else:
                self.request.session.flash(u'パフォーマンスを非公開にしました')
            return render_to_response('ticketing:templates/refresh.html', {}, request=self.request)

        return {
            'form':f,
            'performance':performance
        }

@view_config(decorator=with_bootstrap, permission="authenticated",
             route_name="performances.mailinfo.index")
def mailinfo_index_view(context, request):
    performance_id = request.matchdict["performance_id"]
    return HTTPFound(request.route_url("performances.mailinfo.edit", performance_id=performance_id, mailtype=MailTypeChoices[0][0]))

@view_defaults(decorator=with_bootstrap, permission="authenticated", 
               route_name="performances.mailinfo.edit", 
               renderer="ticketing:templates/performances/mailinfo/new.html")
class MailInfoNewView(BaseView):
    @view_config(request_method="GET")
    def mailinfo_new(self):
        performance = Performance.filter_by(id=self.request.matchdict["performance_id"]).first()
        if performance is None:
            raise HTTPNotFound('performance id %s is not found' % self.request.matchdict["performance_id"])

        template = MailInfoTemplate(self.request, performance.event.organization)
        choice_form = template.as_choice_formclass()()
        formclass = template.as_formclass()
        mailtype = self.request.matchdict["mailtype"]
        form = formclass(**(performance.extra_mailinfo.data.get(mailtype, {}) if performance.extra_mailinfo else {}))
        return {"performance": performance, 
                "form": form, 
                "organization": performance.event.organization, 
                "mailtype": self.request.matchdict["mailtype"], 
                "choices": MailTypeChoices, 
                "choice_form": choice_form}

    @view_config(request_method="POST")
    def mailinfo_new_post(self):
        logger.debug("mailinfo.post: %s" % self.request.POST)
        mutil = get_mail_utility(self.request, self.request.matchdict["mailtype"])

        performance = Performance.filter_by(id=self.request.matchdict["performance_id"]).first()
        if performance is None:
            raise HTTPNotFound('performance id %s is not found' % self.request.matchdict["performance_id"])

        template = MailInfoTemplate(self.request, performance.event.organization)
        choice_form = template.as_choice_formclass()()
        formclass = template.as_formclass()
        form = formclass(self.request.POST)
        if not form.validate():
            self.request.session.flash(u"入力に誤りがあります。")
        else:
            mailtype = self.request.matchdict["mailtype"]
            mailinfo = mutil.create_or_update_mailinfo(self.request, form.as_mailinfo_data(), performance=performance, kind=mailtype)
            logger.debug("mailinfo.data: %s" % mailinfo.data)
            DBSession.add(mailinfo)
            self.request.session.flash(u"メールの付加情報を登録しました")

        return {"performance": performance, 
                "form": form, 
                "organization": performance.event.organization, 
                "mailtype": self.request.matchdict["mailtype"], 
                "choices": MailTypeChoices, 
                "choice_form": choice_form}
