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
from paste.util.multidict import MultiDict

from altair.sqlahelper import get_db_session

from altair.app.ticketing.models import merge_session_with_post, record_to_multidict
from altair.app.ticketing.views import BaseView
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.events.performances.forms import PerformanceForm, PerformancePublicForm
from altair.app.ticketing.core.models import Event, Performance, Order, Venue
from altair.app.ticketing.core.models import PerformanceSetting
from altair.app.ticketing.products.forms import ProductForm
from altair.app.ticketing.orders.forms import OrderForm, OrderSearchForm
from altair.app.ticketing.venues.api import get_venue_site_adapter

from altair.app.ticketing.mails.forms import MailInfoTemplate
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.mails.api import get_mail_utility
from altair.app.ticketing.core.models import MailTypeChoices
from altair.app.ticketing.orders.api import OrderSummarySearchQueryBuilder, QueryBuilderError
from altair.app.ticketing.orders.models import OrderSummary
from altair.app.ticketing.carturl.api import get_cart_url_builder, get_cart_now_url_builder

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

    def build_data_source(self, query_option=None):
        query = {u'n':u'seats|stock_types|stock_holders|stocks'}
        query.update(query_option or dict())
        return dict(
            drawing=get_venue_site_adapter(self.request, self.performance.venue.site).direct_drawing_url,
            metadata=self.request.route_path(
                'api.get_seats',
                venue_id=self.performance.venue.id,
                _query=query
                )
            )

    def _tab_seat_allocation(self):
        return dict(
            data_source=self.build_data_source()
            )

    def _tab_product(self):
        return dict()

    def _tab_order(self):
        slave_session = get_db_session(self.request, name="slave")
        query = slave_session.query(OrderSummary).filter_by(organization_id=self.context.user.organization_id, performance_id=self.performance.id, deleted_at=None)
        form_search = OrderSearchForm(
            self.request.params,
            event_id=self.performance.event_id,
            performance_id=self.performance.id)
        if form_search.validate():
            try:
                query = OrderSummarySearchQueryBuilder(form_search.data, lambda key: form_search[key].label.text)(query)
            except QueryBuilderError as e:
                self.request.session.flash(e.message)
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
        return dict(
            sales_segments=self.performance.sales_segments
            )

    def _tab_reservation(self):
        return dict(
            data_source=self.build_data_source({u'f':u'sale_only'})
            )

    def _extra_data(self):
        # プリンターAPI
        return dict(
            endpoints=dict(
                (key, self.request.route_path('tickets.printer.api.%s' % key))
                for key in ['formats', 'peek', 'dequeue']
                )
            )

    @view_config(route_name='performances.show', renderer='altair.app.ticketing:templates/performances/show.html', permission='event_viewer')
    @view_config(route_name='performances.show_tab', renderer='altair.app.ticketing:templates/performances/show.html', permission='event_viewer')
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

        ## cart url
        cart_url = get_cart_url_builder(self.request).build(self.request, self.performance.event, self.performance)
        data["cart_url"] = cart_url
        data["cart_now_cart_url"] = get_cart_now_url_builder(self.request).build(self.request, cart_url, self.performance.event_id)
        return data


@view_defaults(decorator=with_bootstrap, permission="event_editor")
class Performances(BaseView):

    @view_config(route_name='performances.index', renderer='altair.app.ticketing:templates/performances/index.html', permission='event_viewer')
    def index(self):
        slave_session = get_db_session(self.request, name="slave")

        event_id = int(self.request.matchdict.get('event_id', 0))
        event = slave_session.query(Event).filter(
            Event.id==event_id,
            Event.organization_id==self.context.user.organization_id).first()

        if event is None:
            return HTTPNotFound('event id %d is not found' % event_id)

        sort = self.request.GET.get('sort', 'Performance.start_on')
        direction = self.request.GET.get('direction', 'asc')
        if direction not in ['asc', 'desc']:
            direction = 'asc'

        query = slave_session.query(Performance).filter(
            Performance.event_id==event_id)
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


    @view_config(route_name='performances.new', request_method='GET', renderer='altair.app.ticketing:templates/performances/edit.html')
    def new_get(self):
        slave_session = get_db_session(self.request, name="slave")
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = slave_session.query(Event).filter(
            Event.id==event_id,
            Event.organization_id==self.context.user.organization_id).first()
        if event is None:
            return HTTPNotFound('event id %d is not found' % event_id)

        f = PerformanceForm(MultiDict(code=event.code), organization_id=self.context.user.organization_id)

        return {
            'form':f,
            'event':event,
            'route_name': u'登録',
            'route_path': self.request.path,
        }

    @view_config(route_name='performances.new', request_method='POST', renderer='altair.app.ticketing:templates/performances/edit.html')
    def new_post(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id, organization_id=self.context.user.organization_id)
        if event is None:
            return HTTPNotFound('event id %d is not found' % event_id)

        f = PerformanceForm(self.request.POST, organization_id=self.context.user.organization_id)
        if f.validate():
            performance = merge_session_with_post(Performance(), f.data)
            PerformanceSetting.create_from_model(performance, f.data)
            performance.event_id = event_id
            performance.create_venue_id = f.data['venue_id']
            performance.save()

            self.request.session.flash(u'パフォーマンスを保存しました')
            return HTTPFound(location=route_path('performances.show', self.request, performance_id=performance.id))
        return {
            'form':f,
            'event':event,
            'route_name': u'登録',
            'route_path': self.request.path,
        }

    @view_config(route_name='performances.edit', request_method='GET', renderer='altair.app.ticketing:templates/performances/edit.html')
    @view_config(route_name='performances.copy', request_method='GET', renderer='altair.app.ticketing:templates/performances/edit.html')
    def edit_get(self):
        if self.request.matched_route.name == 'performances.edit':
            route_name = u'編集'
        else:
            route_name = u'コピー'
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
        D = record_to_multidict(performance)
        setting = performance.setting
        if setting:
            D.update((k, getattr(setting, k)) for k in setting.KEYS)
        f.process(D)
        if is_copy:
            f.original_id.data = f.id.data
            f.id.data = None

        return {
            'form':f,
            'event':performance.event,
            'route_name': route_name,
            'route_path': self.request.path,
        }

    @view_config(route_name='performances.edit', request_method='POST', renderer='altair.app.ticketing:templates/performances/edit.html')
    @view_config(route_name='performances.copy', request_method='POST', renderer='altair.app.ticketing:templates/performances/edit.html')
    def edit_post(self):
        if self.request.matched_route.name == 'performances.edit':
            route_name = u'編集'
        else:
            route_name = u'コピー'
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
                try:
                    query = Performance.query.filter_by(id=performance_id)
                    performance = query.with_lockmode('update').populate_existing().one()
                except Exception, e:
                    logging.info(e.message)
                    f.id.errors.append(u'エラーが発生しました。同時に同じ公演を編集することはできません。')
                    return {
                        'form': f,
                        'event': performance.event,
                        'route_name': route_name,
                        'route_path': self.request.path,
                        }

                performance = merge_session_with_post(performance, f.data)
                venue = performance.venue
                if f.data['venue_id'] != venue.id:
                    performance.delete_venue_id = venue.id
                    performance.create_venue_id = f.data['venue_id']
                PerformanceSetting.update_from_model(performance, f.data)

            performance.save()
            self.request.session.flash(u'パフォーマンスを保存しました')
            return HTTPFound(location=route_path('performances.show', self.request, performance_id=performance.id))
        else:
            return {
                'form':f,
                'event':performance.event,
                'route_name': route_name,
                'route_path': self.request.path,
            }

    @view_config(route_name='performances.delete')
    def delete(self):
        performance_id = int(self.request.matchdict.get('performance_id', 0))
        performance = Performance.get(performance_id, self.context.user.organization_id)
        if performance is None:
            return HTTPNotFound('performance id %d is not found' % performance_id)

        location = route_path('events.show', self.request, event_id=performance.event_id)
        try:
            performance.delete()
            self.request.session.flash(u'パフォーマンスを削除しました')
        except Exception, e:
            self.request.session.flash(e.message)
            raise HTTPFound(location=route_path('performances.show', self.request, performance_id=performance.id))

        return HTTPFound(location=location)

    @view_config(route_name='performances.open', request_method='GET',renderer='altair.app.ticketing:templates/performances/_form_open.html')
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

    @view_config(route_name='performances.open', request_method='POST',renderer='altair.app.ticketing:templates/performances/_form_open.html')
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
            return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)

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
               renderer="altair.app.ticketing:templates/performances/mailinfo/new.html")
class MailInfoNewView(BaseView):
    @view_config(request_method="GET")
    def mailinfo_new(self):
        performance = Performance.filter_by(id=self.request.matchdict["performance_id"]).first()
        if performance is None:
            raise HTTPNotFound('performance id %s is not found' % self.request.matchdict["performance_id"])

        mutil = get_mail_utility(self.request, self.request.matchdict["mailtype"])
        template = MailInfoTemplate(self.request, performance.event.organization, mutil=mutil)
        choice_form = template.as_choice_formclass()()
        formclass = template.as_formclass()
        mailtype = self.request.matchdict["mailtype"]
        form = formclass(**(performance.extra_mailinfo.data.get(mailtype, {}) if performance.extra_mailinfo else {}))
        return {"performance": performance, 
                "form": form, 
                "organization": performance.event.organization, 
                "mailtype": self.request.matchdict["mailtype"], 
                "choices": MailTypeChoices, 
                "mutil": mutil, 
                "choice_form": choice_form}

    @view_config(request_method="POST")
    def mailinfo_new_post(self):
        logger.debug("mailinfo.post: %s" % self.request.POST)
        mutil = get_mail_utility(self.request, self.request.matchdict["mailtype"])

        performance = Performance.filter_by(id=self.request.matchdict["performance_id"]).first()
        if performance is None:
            raise HTTPNotFound('performance id %s is not found' % self.request.matchdict["performance_id"])

        template = MailInfoTemplate(self.request, performance.event.organization, mutil=mutil)
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
                "mutil": mutil, 
                "choices": MailTypeChoices, 
                "choice_form": choice_form}
