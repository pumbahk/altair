# -*- coding: utf-8 -*-

import sys
import re
import logging
from cStringIO import StringIO

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
from altair.app.ticketing.events.performances.forms import PerformanceForm, PerformancePublicForm, OrionPerformanceForm
from altair.app.ticketing.core.models import Event, Performance, PerformanceSetting, OrionPerformance
from altair.app.ticketing.orders.forms import OrderForm, OrderSearchForm, OrderImportForm
from altair.app.ticketing.venues.api import get_venue_site_adapter

from altair.app.ticketing.mails.forms import MailInfoTemplate
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.mails.api import get_mail_utility
from altair.app.ticketing.core.models import MailTypeChoices
from altair.app.ticketing.orders.api import OrderSummarySearchQueryBuilder, QueryBuilderError
from altair.app.ticketing.orders.models import OrderSummary, OrderImportTask, ImportStatusEnum, ImportTypeEnum
from altair.app.ticketing.orders.importer import OrderImporter, ImportCSVReader
from altair.app.ticketing.orders import helpers as order_helpers
from altair.app.ticketing.carturl.api import get_cart_url_builder, get_cart_now_url_builder
from altair.app.ticketing.events.sales_segments.resources import (
    SalesSegmentAccessor,
)
from .api import set_visible_performance, set_invisible_performance

logger = logging.getLogger(__name__)

@view_defaults(decorator=with_bootstrap, permission='event_editor', renderer='altair.app.ticketing:templates/performances/show.html')
class PerformanceShowView(BaseView):
    IMPORT_ERRORS_KEY = '%s.import_errors' % __name__

    def __init__(self, context, request):
        super(PerformanceShowView, self).__init__(context, request)
        self.performance = self.context.performance

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
                query._request = self.request
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
            form_order=OrderForm(event_id=self.performance.event_id, context=self.context)
            )

    def _tab_summary(self):
        return dict(
            sales_segments=self.performance.sales_segments
            )

    def _tab_reservation(self):
        # todo: performance_id まで指定してもいいが、OrderSearchForm をキレイにするほうが方針として良さそう
        return dict(
            data_source=self.build_data_source({u'f':u'sale_only'}),
            form_search=OrderSearchForm(self.request.params, event_id=self.performance.event_id)
            )

    def _extra_data(self):
        # プリンターAPI
        data = dict(
            endpoints=dict(
                (key, self.request.route_path('tickets.printer.api.%s' % key))
                for key in ['formats', 'peek', 'dequeue']
                )
            )

        ## cart url
        cart_url = get_cart_url_builder(self.request).build(self.request, self.performance.event, self.performance)
        data.update(dict(
            cart_url=cart_url,
            cart_now_cart_url=get_cart_now_url_builder(self.request).build(self.request, cart_url, self.performance.event_id)
        ))
        return data

    @view_config(route_name='performances.visible', permission='event_editor')
    def visible_performance(self):
        set_visible_performance(self.request)
        return HTTPFound(self.request.route_path("performances.index", event_id=self.context.event.id))

    @view_config(route_name='performances.invisible', permission='event_editor')
    def invisible_performance(self):
        set_invisible_performance(self.request)
        return HTTPFound(self.request.route_path("performances.index", event_id=self.context.event.id))

    @view_config(route_name='performances.show', permission='event_viewer')
    @view_config(route_name='performances.show_tab', permission='event_viewer')
    def show(self):
        tab = self.request.matchdict.get('tab', 'summary')
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

    @view_config(route_name='performances.import_orders.index', request_method='GET')
    def import_orders_get(self):
        importer = self.request.session.get('ticketing.order.importer')
        if importer:
            del self.request.session['ticketing.order.importer']

        order_import_tasks = OrderImportTask.query.filter(
            OrderImportTask.organization_id==self.context.organization.id,
            OrderImportTask.performance_id==self.performance.id,
            OrderImportTask.status != ImportStatusEnum.ConfirmNeeded.v
        ).all()

        data = {
            'tab': 'import_orders',
            'performance': self.performance,
            'form': OrderImportForm(always_issue_order_no=True, merge_order_attributes=True),
            'oh': order_helpers,
            'order_import_tasks':order_import_tasks
        }
        data.update(self._extra_data())
        return data

    @view_config(route_name='performances.import_orders.index', request_method='POST')
    def import_orders_post(self):
        f = OrderImportForm(self.request.params)
        if not f.validate():
            for f, errors in f.errors.items():
                for error in errors:
                    self.request.session.flash(error)
            return self.import_orders_get()
        importer = OrderImporter(
            self.request,
            import_type=f.import_type.data | (ImportTypeEnum.AlwaysIssueOrderNo.v if f.always_issue_order_no.data else 0),
            allocation_mode=f.allocation_mode.data,
            merge_order_attributes=f.merge_order_attributes.data,
            session=DBSession
            )
        order_import_task, errors = importer(
            reader=ImportCSVReader(StringIO(f.order_csv.data.value)),
            operator=self.context.user,
            organization=self.context.organization,
            performance=self.performance
            )
        self.request.session[self.IMPORT_ERRORS_KEY] = dict(
            (
                order_no, [
                    {
                        'level': error.level,
                        'message': (u'%s (%d行目)' % (error.message, error.line_num) if hasattr(error, 'line_num') else error.message)
                        }
                    for error in errors_for_order
                    ]
                )
            for order_no, errors_for_order in errors.items()
            )
        DBSession.add(order_import_task)
        DBSession.flush()
        return HTTPFound(self.request.route_url('performances.import_orders.confirm', performance_id=self.performance.id, _query=dict(task_id=order_import_task.id)))

    @view_config(route_name='performances.import_orders.confirm', request_method='GET')
    def import_orders_confirm_get(self):
        task_id = None
        try:
            task_id = long(self.request.params.get('task_id'))
        except (ValueError, TypeError):
            pass
        if task_id is None:
            self.request.session.flash(u'不明なエラーです')
            return HTTPFound(self.request.route_url('performances.import_orders.index', performance_id=self.performance.id))
        task = OrderImportTask.query.filter_by(id=task_id).one()
        data = {
            'tab': 'import_orders',
            'action': 'confirm',
            'performance': self.performance,
            'oh': order_helpers,
            'task': task,
            'errors': self.request.session.get(self.IMPORT_ERRORS_KEY, {}),
            'stats': order_helpers.order_import_task_stats(task),
        }
        data.update(self._extra_data())
        return data

    @view_config(route_name='performances.import_orders.confirm', request_method='POST')
    def import_orders_confirm_post(self):
        task_id = None
        try:
            task_id = long(self.request.params.get('task_id'))
        except (ValueError, TypeError):
            pass
        if task_id is None:
            self.request.session.flash(u'不明なエラーです')
            return HTTPFound(self.request.route_url('performances.import_orders.index', performance_id=self.performance.id))
        task = OrderImportTask.query.filter_by(id=task_id).one()
        if task.count > 0:
            task.status = ImportStatusEnum.Waiting.v
            self.request.session.flash(u'予約インポートを実行しました')
            return HTTPFound(self.request.route_url('performances.import_orders.index', performance_id=self.performance.id))
        else:
            self.request.session.flash(u'インポート対象がありません')
            return HTTPFound(self.request.route_url('performances.import_orders.index', performance_id=self.performance.id))

    @view_config(route_name='performances.import_orders.show')
    def import_orders_show(self):
        task_id = self.request.matchdict.get('task_id')
        task = OrderImportTask.query.filter(
            OrderImportTask.id==task_id,
            OrderImportTask.organization_id==self.context.organization.id
        ).first()
        if task is None:
            return HTTPFound(self.request.route_url('performances.import_orders.index', performance_id=self.performance.id))
        data = {
            'tab': 'import_orders',
            'action': 'show',
            'performance': self.performance,
            'oh': order_helpers,
            'task': task,
            'errors': task.errors,
            'stats': order_helpers.order_import_task_stats(task),
        }
        data.update(self._extra_data())
        return data

    @view_config(route_name='performances.import_orders.delete')
    def import_orders_delete(self):
        task_id = self.request.matchdict.get('task_id')
        task = OrderImportTask.query.filter(
            OrderImportTask.id==task_id,
            OrderImportTask.organization_id==self.context.organization.id
        ).first()
        if task and task.status == ImportStatusEnum.Importing.v:
            self.request.session.flash(u'既にインポート中のため、削除できません')
        else:
            task.delete()
            self.request.session.flash(u'予約インポートを削除しました')
        return HTTPFound(self.request.route_url('performances.import_orders.index', performance_id=self.performance.id))

    @view_config(route_name="performances.orion.index", request_method='GET')
    def orion_index_view(self):
        form = OrionPerformanceForm(
            self.request.params,
            data=self.performance.orion)
        if self.performance.orion is not None:
            form.enabled.data = True
            if self.performance.orion.coupon_2_name is not None:
                form.coupon_2_enabled.data = True

        data = {
            'tab': 'orion',
            'action': '',
            'performance': self.performance,
            'form' : form,
        }
        return data

    @view_config(route_name="performances.orion.index", request_method='POST')
    def orion_index_update(self):
        form = OrionPerformanceForm(self.request.params)

        if form.coupon_2_enabled.data == False or form.coupon_2_name.data is None or form.coupon_2_name.data == "":
            form.coupon_2_name.data = None
            form.coupon_2_qr_enabled.data = None
            form.coupon_2_pattern.data = None

        if form.validate():
            if form.enabled.data == False:
                # delete
                if self.performance.orion != None:
                    self.performance.orion.delete()
            elif self.performance.orion is None:
                # insert
                op = merge_session_with_post(
                    OrionPerformance(
                        performance_id=self.performance.id
                    ),
                    form.data
                )
                op.save()
            else:
                # update
                op = merge_session_with_post(
                    self.performance.orion,
                    form.data
                )
                op.save()

            return HTTPFound(self.request.route_url('performances.orion.index', performance_id=self.performance.id))

        return self.orion_index_view()


@view_defaults(decorator=with_bootstrap, permission="event_editor")
class Performances(BaseView):

    @view_config(route_name='performances.index', renderer='altair.app.ticketing:templates/performances/index.html', permission='event_viewer')
    def index(self):
        slave_session = get_db_session(self.request, name="slave")

        sort = self.request.GET.get('sort', 'Performance.start_on')
        direction = self.request.GET.get('direction', 'asc')
        if direction not in ['asc', 'desc']:
            direction = 'asc'

        query = slave_session.query(Performance) \
            .join(PerformanceSetting, Performance.id == PerformanceSetting.performance_id) \
            .filter(Performance.event_id==self.context.event.id)

        if self.request.params.get('format') == 'xml':
            event_query = slave_session.query(Event).filter(Event.id==self.context.event.id)
            return self.index_xml(event_query, query)

        from . import VISIBLE_PERFORMANCE_SESSION_KEY
        if not self.request.session.get(VISIBLE_PERFORMANCE_SESSION_KEY):
            query = query.filter(PerformanceSetting.visible==True)
        query = query.order_by(Performance.display_order)
        query = query.order_by(sort + ' ' + direction)

        performances = paginate.Page(
            query,
            page=int(self.request.params.get('page', 0)),
            items_per_page=20,
            url=paginate.PageURL_WebOb(self.request)
        )

        return {
            'event':self.context.event,
            'performances':performances,
            'form':PerformanceForm(organization_id=self.context.user.organization_id),
        }

    def index_xml(self, event_query, query):
        import xml.etree.ElementTree as ElementTree
        from pyramid.response import Response

        e = event_query.one()

        root = ElementTree.Element('Result')
        event = ElementTree.SubElement(root, 'Event')
        ElementTree.SubElement(event, 'Code').text = e.code
        ElementTree.SubElement(event, 'Title').text = e.title
        for p in query.all():
            performance = ElementTree.SubElement(root, 'Performance')
            ElementTree.SubElement(performance, 'Code').text = p.code
            ElementTree.SubElement(performance, 'DateTime').text = str(p.start_on)
            ElementTree.SubElement(performance, 'Name').text = p.name
            ElementTree.SubElement(performance, 'Site').text = p.venue.name

        return Response(ElementTree.tostring(root), headers=[ ('Content-Type', 'text/xml') ])

    @view_config(route_name='performances.new', request_method='GET', renderer='altair.app.ticketing:templates/performances/edit.html')
    def new_get(self):
        f = PerformanceForm(MultiDict(code=self.context.event.code, visible=True), organization_id=self.context.user.organization_id)
        return {
            'form':f,
            'event':self.context.event,
            'route_name': u'登録',
            'route_path': self.request.path,
        }

    @view_config(route_name='performances.new', request_method='POST', renderer='altair.app.ticketing:templates/performances/edit.html')
    def new_post(self):
        f = PerformanceForm(self.request.POST, organization_id=self.context.user.organization_id, event=self.context.event, visible=True)
        if f.validate():
            performance = merge_session_with_post(
                Performance(
                    setting=PerformanceSetting(
                        order_limit=f.order_limit.data,
                        entry_limit=f.entry_limit.data,
                        max_quantity_per_user=f.max_quantity_per_user.data,
                        visible=True,
                        ),
                    event_id=self.context.event.id
                    ),
                f.data
                )
            performance.create_venue_id = f.venue_id.data
            performance.save()
            event = performance.event
            accessor = SalesSegmentAccessor()
            for ssg in event.sales_segment_groups:
                accessor.create_sales_segment_for_performance(ssg, performance)
            self.request.session.flash(u'パフォーマンスを保存しました')
            return HTTPFound(location=route_path('performances.show', self.request, performance_id=performance.id))
        return {
            'form':f,
            'event':self.context.event,
            'route_name': u'登録',
            'route_path': self.request.path,
        }

    @view_config(route_name='performances.edit', request_method='GET', renderer='altair.app.ticketing:templates/performances/edit.html')
    @view_config(route_name='performances.copy', request_method='GET', renderer='altair.app.ticketing:templates/performances/edit.html')
    def edit_get(self):
        performance = self.context.performance
        if self.request.matched_route.name == 'performances.edit':
            route_name = u'編集'
        else:
            route_name = u'コピー'

        is_copy = (self.request.matched_route.name == 'performances.copy')
        f = PerformanceForm(
            obj=performance,
            organization_id=self.context.user.organization_id,
            venue_id=performance.venue.id
            )
        f.order_limit.data = performance.setting and performance.setting.order_limit
        f.entry_limit.data = performance.setting and performance.setting.entry_limit
        f.max_quantity_per_user.data = performance.setting and performance.setting.max_quantity_per_user
        f.visible.data = performance.setting and performance.setting.visible
        if is_copy:
            f.original_id.data = f.id.data
            f.id.data = None

        return {
            'form':f,
            'is_copy':is_copy,
            'event':performance.event,
            'route_name': route_name,
            'route_path': self.request.path,
        }

    @view_config(route_name='performances.edit', request_method='POST', renderer='altair.app.ticketing:templates/performances/edit.html')
    @view_config(route_name='performances.copy', request_method='POST', renderer='altair.app.ticketing:templates/performances/edit.html')
    def edit_post(self):
        performance = self.context.performance
        if self.request.matched_route.name == 'performances.edit':
            route_name = u'編集'
        else:
            route_name = u'コピー'

        is_copy = (self.request.matched_route.name == 'performances.copy')
        f = PerformanceForm(
            self.request.POST,
            organization_id=self.context.user.organization_id,
            event=performance.event,
            venue_id=performance.venue.id
            )
        if f.validate():
            if is_copy:
                event_id = performance.event_id
                performance = merge_session_with_post(Performance(), f.data)
                performance.event_id = event_id
                performance.create_venue_id = f.venue_id.data
                if performance.setting is None:
                    performance.setting = PerformanceSetting()
                performance.setting.order_limit = f.order_limit.data
                performance.setting.entry_limit = f.entry_limit.data
                performance.setting.max_quantity_per_user = f.max_quantity_per_user.data
                performance.setting.visible = f.visible.data

                original = Performance.query.filter_by(id=self.request.POST['original_id']).first()
                if original is not None:
                    if original.orion is not None:
                        performance.orion = OrionPerformance.clone(original.orion, False, [ 'performance_id' ])
            else:
                try:
                    query = Performance.query.filter_by(id=performance.id)
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
                if performance.setting is None:
                    performance.setting = PerformanceSetting()
                performance.setting.order_limit = f.order_limit.data
                performance.setting.entry_limit = f.entry_limit.data
                performance.setting.max_quantity_per_user = f.max_quantity_per_user.data
                performance.setting.visible = f.visible.data

            performance.save()
            self.request.session.flash(u'パフォーマンスを保存しました')
            return HTTPFound(location=route_path('performances.show', self.request, performance_id=performance.id))
        else:
            return {
                'form':f,
                'is_copy':False,
                'event':performance.event,
                'route_name': route_name,
                'route_path': self.request.path,
            }

    @view_config(route_name='performances.delete')
    def delete(self):
        performance = self.context.performance
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
        f = PerformancePublicForm(record_to_multidict(self.context.performance))
        f.public.data = 0 if f.public.data == 1 else 1

        return {
            'form':f,
            'performance':self.context.performance,
        }

    @view_config(route_name='performances.open', request_method='POST',renderer='altair.app.ticketing:templates/performances/_form_open.html')
    def open_post(self):
        f = PerformancePublicForm(self.request.POST)

        if f.validate():
            performance = merge_session_with_post(self.context.performance, f.data)
            performance.save()

            if performance.public:
                self.request.session.flash(u'パフォーマンスを公開しました')
            else:
                self.request.session.flash(u'パフォーマンスを非公開にしました')
            return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)

        return {
            'form':f,
            'performance':self.context.performance,
        }

@view_config(decorator=with_bootstrap, permission="event_editor",
             route_name="performances.mailinfo.index")
def mailinfo_index_view(context, request):
    return HTTPFound(request.route_url("performances.mailinfo.edit", performance_id=context.performance.id, mailtype=MailTypeChoices[0][0]))

@view_defaults(decorator=with_bootstrap, permission="event_editor",
               route_name="performances.mailinfo.edit",
               renderer="altair.app.ticketing:templates/performances/mailinfo/new.html")
class MailInfoNewView(BaseView):
    @view_config(request_method="GET")
    def mailinfo_new(self):
        performance = self.context.performance
        mutil = get_mail_utility(self.request, self.request.matchdict["mailtype"])
        template = MailInfoTemplate(self.request, performance.event.organization, mutil=mutil)
        choice_form = template.as_choice_formclass()()
        formclass = template.as_formclass()
        mailtype = self.request.matchdict["mailtype"]
        form = formclass(**(performance.extra_mailinfo.data.get(mailtype, {}) if performance.extra_mailinfo else {}))
        return {"performance": performance,
                "form": form,
                "organization": performance.event.organization,
                "extra_mailinfo": performance.extra_mailinfo,
                "mailtype": self.request.matchdict["mailtype"],
                "choices": MailTypeChoices,
                "mutil": mutil,
                "choice_form": choice_form}

    @view_config(request_method="POST")
    def mailinfo_new_post(self):
        logger.debug("mailinfo.post: %s" % self.request.POST)
        mutil = get_mail_utility(self.request, self.request.matchdict["mailtype"])
        performance = self.context.performance

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
