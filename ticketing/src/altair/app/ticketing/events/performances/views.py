# -*- coding: utf-8 -*-

import sys
import re

import logging
import datetime
from cStringIO import StringIO

import webhelpers.paginate as paginate
import altair.app.ticketing.discount_code.api as dc_api
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPBadRequest
from pyramid.url import route_path
from pyramid.renderers import render_to_response
from pyramid.security import has_permission, ACLAllowed
from paste.util.multidict import MultiDict

from altair.sqlahelper import get_db_session

from altair.app.ticketing.models import merge_session_with_post, record_to_multidict
from altair.app.ticketing.views import BaseView
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.events.performances.forms import (
    PerformanceForm,
    PerformanceManycopyForm,
    PerformanceTermForm,
    PerformancePublicForm,
    OrionPerformanceForm,
    PerformanceResaleSegmentForm,
    PerformanceResaleRequestSearchForm
)
from altair.app.ticketing.core.models import Event, Performance, PerformanceSetting, OrionPerformance, Stock_drawing_l0_id
from altair.app.ticketing.famiport.userside_models import AltairFamiPortPerformance
from altair.app.ticketing.orders.forms import OrderForm, OrderSearchForm, OrderImportForm
from altair.app.ticketing.venues.api import get_venue_site_adapter
from altair.app.ticketing.lots.api import copy_lots_between_performance, copy_lot_products_from_performance

from altair.app.ticketing.mails.forms import MailInfoTemplate
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.mails.api import get_mail_utility
from altair.app.ticketing.core.models import MailTypeChoices
from altair.app.ticketing.orders.api import OrderSummarySearchQueryBuilder, QueryBuilderError
from altair.app.ticketing.orders.models import OrderSummary, OrderImportTask, ImportStatusEnum, ImportTypeEnum, OrderedProductItemToken, OrderedProductItem, OrderedProduct, Order
from altair.app.ticketing.orders.importer import OrderImporter, ImportCSVReader
from altair.app.ticketing.orders import helpers as order_helpers
from altair.app.ticketing.cart import helpers as cart_helper
from altair.app.ticketing.carturl.api import get_performance_cart_url_builder, get_performance_spa_cart_url_builder, get_cart_now_url_builder
from altair.app.ticketing.events.sales_segments.resources import (
    SalesSegmentAccessor,
)
from altair.app.ticketing.resale.models import ResaleSegment, ResaleRequest, SentStatus, ResaleRequestStatus
from .generator import PerformanceCodeGenerator
from ..famiport_helpers import get_famiport_performance_ids
from .api import (set_visible_performance,
                  set_invisible_performance,
                  send_resale_segment,
                  send_all_resale_request,
                  send_resale_request)

from altair.app.ticketing.discount_code.forms import DiscountCodeSettingForm

logger = logging.getLogger(__name__)


@view_defaults(decorator=with_bootstrap, permission='reservation_editor',
               renderer='altair.app.ticketing:templates/reservation/reservation.html')
class ReservationView(BaseView):

    def __init__(self, context, request):
        super(ReservationView, self).__init__(context, request)
        self.performance = self.context.performance

    @view_config(route_name='performances.reservation')
    def reservation(self):
        query = {u'n': u'seats|stock_types|stock_holders|stocks'}
        query.update({u'f': u'sale_only'} or dict())
        data_source = dict(
            drawing=get_venue_site_adapter(
                self.request, self.performance.venue.site).direct_drawing_url,
            metadata=self.request.route_path(
                'api.get_seats',
                venue_id=self.performance.venue.id,
                _query=query
            )
        )

        data = {
            'performance': self.performance,
            'form_search': OrderSearchForm(
                self.request.params, event_id=self.performance.event_id),
            'data_source': data_source,
            'endpoints': dict(
                (key, self.request.route_path('tickets.printer.api.%s' % key))
                for key in ['formats', 'peek', 'dequeue']
            )
        }
        return data


@view_defaults(decorator=with_bootstrap, permission='event_editor', renderer='altair.app.ticketing:templates/performances/show.html')
class PerformanceShowView(BaseView):
    IMPORT_ERRORS_KEY = '%s.import_errors' % __name__

    def __init__(self, context, request):
        super(PerformanceShowView, self).__init__(context, request)
        self.performance = self.context.performance

    def build_data_source(self, query_option=None):
        query = {u'n': u'seats|stock_types|stock_holders|stocks'}
        query.update(query_option or dict())
        return dict(
            drawing=get_venue_site_adapter(
                self.request, self.performance.venue.site).direct_drawing_url,
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
        query = slave_session.query(OrderSummary).filter_by(
            organization_id=self.context.user.organization_id, performance_id=self.performance.id, deleted_at=None)
        form_search = OrderSearchForm(
            self.request.params,
            event_id=self.performance.event_id,
            performance_id=self.performance.id)
        if form_search.validate():
            try:
                query = OrderSummarySearchQueryBuilder(
                    form_search.data, lambda key: form_search[key].label.text)(query)
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
            form_order=OrderForm(
                event_id=self.performance.event_id, context=self.context)
        )

    def _tab_summary(self):
        return dict(
            sales_segments=self.performance.sales_segments
        )

    def _tab_reservation(self):
        # todo: performance_id まで指定してもいいが、OrderSearchForm をキレイにするほうが方針として良さそう
        return dict(
            data_source=self.build_data_source({u'f': u'sale_only'}),
            form_search=OrderSearchForm(
                self.request.params, event_id=self.performance.event_id)
        )

    def _extra_data(self):
        # プリンターAPI
        data = dict(
            endpoints=dict(
                (key, self.request.route_path('tickets.printer.api.%s' % key))
                for key in ['formats', 'peek', 'dequeue']
            )
        )

        # cart url
        cart_url = get_performance_cart_url_builder(self.request).build(
            self.request, self.performance)
        spa_cart_url = None
        cart_now_spa_cart_url = None
        if self.context.organization.code == 'RE':
            spa_cart_url = get_performance_spa_cart_url_builder(self.request).build(
                self.request, self.performance)
            cart_now_spa_cart_url = get_cart_now_url_builder(self.request).build(
                self.request, spa_cart_url, self.performance.event_id)

        data.update(dict(
            cart_url=cart_url,
            spa_cart_url =spa_cart_url,
            cart_now_cart_url=get_cart_now_url_builder(self.request).build(
                self.request, cart_url, self.performance.event_id),
            cart_now_spa_cart_url=cart_now_spa_cart_url,
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
        self.context.sort_sales_segments()

        data = {
            'performance': self.performance,
            'tab': tab
        }

        tab_method = '_tab_' + tab.replace('-', '_')
        if not hasattr(self, tab_method):
            logger.warning(
                "AttributeError: 'PerformanceShowView' object has no attribute '{0}'".format(tab_method))
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
            OrderImportTask.organization_id == self.context.organization.id,
            OrderImportTask.performance_id == self.performance.id,
            OrderImportTask.status != ImportStatusEnum.ConfirmNeeded.v
        ).all()

        data = {
            'tab': 'import_orders',
            'performance': self.performance,
            'form': OrderImportForm(
                always_issue_order_no=False,
                merge_order_attributes=True,
                enable_random_import=True,
            ),
            'oh': order_helpers,
            'order_import_tasks': order_import_tasks
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
            import_type=f.import_type.data | (
                ImportTypeEnum.AlwaysIssueOrderNo.v if f.always_issue_order_no.data else 0),
            allocation_mode=f.allocation_mode.data,
            merge_order_attributes=f.merge_order_attributes.data,
            enable_random_import=f.enable_random_import.data,
            session=DBSession
        )
        order_import_task, errors = importer(
            reader=ImportCSVReader(StringIO(f.order_csv.data.value), encoding='cp932:normalized-tilde'),
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
            OrderImportTask.id == task_id,
            OrderImportTask.organization_id == self.context.organization.id
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
            OrderImportTask.id == task_id,
            OrderImportTask.organization_id == self.context.organization.id
        ).first()
        if task and task.status == ImportStatusEnum.Importing.v:
            self.request.session.flash(u'既にインポート中のため、削除できません')
        else:
            task.delete()
            self.request.session.flash(u'予約インポートを削除しました')
        return HTTPFound(self.request.route_url('performances.import_orders.index', performance_id=self.performance.id))

    @view_config(route_name="performances.region.index", request_method='GET')
    def region_index_view(self):
        data = {
            'tab': 'region',
            'action': '',
            'performance': self.performance,
            'stock_types': self.performance.stock_types,
            'stock_holders': self.performance.event.stock_holders,
            'products': self.performance.products,
        }
        return data

    @view_config(route_name="performances.region.update", request_method='POST')
    def region_update(self):
        # convert to set
        update = set()
        for k, v in self.request.params.items():
            m = re.match('(\d+)\[\]', k)
            if m and v != '':
                update.add((int(m.group(1)), v))

        for stock_type in self.performance.stock_types:
            for stock in stock_type.stocks:
                if stock.performance.id == self.performance.id and stock.stock_holder:
                    for stock_drawing_l0_id in stock.stock_drawing_l0_ids:
                        drawing_l0_id = stock_drawing_l0_id.drawing_l0_id
                        if (stock.id, drawing_l0_id) in update:
                            update.remove((stock.id, drawing_l0_id))
                        else:
                            # Should remove from db
                            DBSession.delete(stock_drawing_l0_id)

        for (stock_id, drawing_l0_id) in update:
            # Should add to db
            DBSession.add(Stock_drawing_l0_id(stock_id=stock_id, drawing_l0_id=drawing_l0_id))

        DBSession.flush()
        self.request.session.flash(u'領域設定を更新しました')
        return HTTPFound(self.request.route_url('performances.region.index', performance_id=self.performance.id))

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
            'form': form,
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

    @view_config(route_name="performances.discount_code_settings.show", request_method='GET',
                 custom_predicates=(dc_api.check_discount_code_functions_available,))
    def discount_code_settings_show(self):
        session = get_db_session(self.request, 'slave')
        query = Performance(id=self.performance.id).find_available_target_settings_query(
            session=session,
            refer_all=True,
            now=self.context.now
        ).group_by('DiscountCodeSetting.id')

        data = {
            'tab': 'discount_code',
            'performance': self.performance,
            'settings': dc_api.paginate_setting_list(query, self.request),
            'form': DiscountCodeSettingForm(),
        }
        return data

    @view_config(route_name="performances.resale.index", request_method='GET')
    def resale_index(self):
        slave_session = get_db_session(self.request, name="slave")
        selected_resale_segment_id = self.request.params.get('resale_segment_id', None)
        form = PerformanceResaleSegmentForm(performance_id=self.performance.id)
        search_form = PerformanceResaleRequestSearchForm(self.request.params)
        resale_segments = slave_session.query(ResaleSegment) \
                                       .filter(ResaleSegment.performance_id == self.performance.id)

        if selected_resale_segment_id:
            resale_segment = resale_segments.filter(id = selected_resale_segment_id).one()
        else:
            resale_segment = resale_segments.first()

        if resale_segment:
            form.resale_segment_id.data = resale_segment.id
            # 現時点resale_segmentは1つしかない。
            resale_requests = slave_session.query(ResaleRequest, OrderedProductItemToken) \
                .filter(ResaleRequest.ordered_product_item_token_id == OrderedProductItemToken.id) \
                .filter(ResaleRequest.resale_segment_id == resale_segment.id) \
                .filter(ResaleRequest.deleted_at == None)
        else:
            resale_requests = []

        if resale_requests:
            if search_form.order_no.data:
                order_no_list = re.split(r'[ \t,]', search_form.order_no.data)
                resale_requests = resale_requests \
                    .join(OrderedProductItemToken,
                          ResaleRequest.ordered_product_item_token_id == OrderedProductItemToken.id) \
                    .join(OrderedProductItem, OrderedProductItem.id == OrderedProductItemToken.ordered_product_item_id) \
                    .join(OrderedProduct, OrderedProduct.id == OrderedProductItem.ordered_product_id) \
                    .join(Order, Order.id == OrderedProduct.order_id) \
                    .filter(Order.order_no.in_(order_no_list))

            if search_form.account_holder_name.data:
                resale_requests = resale_requests.filter(ResaleRequest.account_holder_name == search_form.account_holder_name.data)

            if search_form.get_status():
                resale_requests = resale_requests.filter(ResaleRequest.status.in_(search_form.get_status()))

            if search_form.get_sent_status():
                resale_requests = resale_requests.filter(ResaleRequest.sent_status.in_(search_form.get_sent_status()))

        resale_requests = paginate.Page(
            resale_requests,
            page=int(self.request.params.get('page', 0)),
            items_per_page=50,
            url=paginate.PageURL_WebOb(self.request)
        )
        return {
            'tab': 'resale',
            'action': '',
            'performance': self.performance,
            'resale_segments': resale_segments.all(),
            'selected_resale_segment_id': selected_resale_segment_id,
            'resale_requests': resale_requests,
            'form': form,
            'search_form': search_form
        }


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
            .outerjoin(PerformanceSetting, Performance.id == PerformanceSetting.performance_id) \
            .filter(Performance.event_id == self.context.event.id)

        if self.request.params.get('format') == 'xml':
            event_query = slave_session.query(Event).filter(
                Event.id == self.context.event.id)
            return self.index_xml(event_query, query)

        from . import VISIBLE_PERFORMANCE_SESSION_KEY
        if not self.request.session.get(VISIBLE_PERFORMANCE_SESSION_KEY):
            query = query.filter(PerformanceSetting.visible == True)
        query = query.order_by(Performance.display_order)
        query = query.order_by(sort + ' ' + direction)

        performances = paginate.Page(
            query,
            page=int(self.request.params.get('page', 0)),
            items_per_page=20,
            url=paginate.PageURL_WebOb(self.request)
        )

        from ..famiport_helpers import get_famiport_reflection_warnings
        warnings = {}
        for p in performances:
            warnings.update(get_famiport_reflection_warnings(self.request, slave_session, p))

        return {
            'event': self.context.event,
            'performances': performances,
            'fm_performance_ids': get_famiport_performance_ids(slave_session, performances),\
            'famiport_reflect_warnings': warnings,
            'form': PerformanceForm(
                        organization_id=self.context.user.organization_id,
                        context=self.context),
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
            ElementTree.SubElement(
                performance, 'DateTime').text = str(p.start_on)
            ElementTree.SubElement(performance, 'Name').text = p.name
            ElementTree.SubElement(performance, 'Site').text = p.venue.name

        return Response(ElementTree.tostring(root), headers=[('Content-Type', 'text/xml')])

    @view_config(route_name='performances.new', request_method='GET', renderer='altair.app.ticketing:templates/performances/edit.html')
    def new_get(self):
        f = PerformanceForm(
            MultiDict(code=self.context.event.code, visible=True),
            organization_id=self.context.user.organization_id,
            context=self.context)

        if self.context.organization.setting.show_event_op_and_sales:
            # 紐づくイベントのevent_operator_idを継承する。event_operator_idがない場合はパフォーマンスを追加するオペーレターのidを入れる
            f.performance_operator_id.data = self.context.event.setting.event_operator_id or self.context.user.id
            # 紐づくイベントのsales_person_idを継承する。ales_person_idがない場合はブランクのままで
            f.sales_person_id.data = self.context.event.setting.sales_person_id

        f.account_id.data = self.context.event.account_id
        return {
            'form': f,
            'event': self.context.event,
            'route_name': u'登録',
            'route_path': self.request.path,
        }

    @view_config(route_name='performances.new', request_method='POST', renderer='altair.app.ticketing:templates/performances/edit.html')
    def new_post(self):
        f = PerformanceForm(
            self.request.POST,
            organization_id=self.context.user.organization_id,
            event=self.context.event,
            context=self.context,
            visible=True)
        if f.validate():
            performance = merge_session_with_post(
                Performance(
                    setting=PerformanceSetting(
                        order_limit=f.order_limit.data,
                        entry_limit=f.entry_limit.data,
                        max_quantity_per_user=f.max_quantity_per_user.data,
                        performance_operator_id=f.performance_operator_id.data,
                        sales_person_id=f.sales_person_id.data,
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
            'form': f,
            'event': self.context.event,
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

        # 配券元が存在しない場合、イベントのものを使う。（既存のパフォーマンスのみ発生TKT-1974）
        if not performance.account_id:
            performance.account_id = performance.event.account_id

        f = PerformanceForm(
            obj=performance,
            organization_id=self.context.user.organization_id,
            venue_id=performance.venue.id,
            context=self.context
        )
        f.order_limit.data = performance.setting and performance.setting.order_limit
        f.entry_limit.data = performance.setting and performance.setting.entry_limit
        f.max_quantity_per_user.data = performance.setting and performance.setting.max_quantity_per_user
        f.performance_operator_id.data = performance.setting and performance.setting.performance_operator_id
        f.sales_person_id.data = performance.setting and performance.setting.sales_person_id
        f.visible.data = performance.setting and performance.setting.visible
        if is_copy:
            f.original_id.data = f.id.data
            f.id.data = None

        return {
            'form': f,
            'is_copy': is_copy,
            'event': performance.event,
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
            venue_id=performance.venue.id,
            context=self.context
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
                performance.setting.performance_operator_id = f.performance_operator_id.data
                performance.setting.sales_person_id = f.sales_person_id.data
                performance.setting.visible = f.visible.data

                original = Performance.query.filter_by(
                    id=self.request.POST['original_id']).first()
                if original is not None:
                    if original.orion is not None:
                        performance.orion = OrionPerformance.clone(
                            original.orion, False, ['performance_id'])
                performance.save()

                # 抽選の商品を作成する
                copy_lots_between_performance(original, performance)
            else:
                try:
                    query = Performance.query.filter_by(id=performance.id)
                    performance = query.with_lockmode(
                        'update').populate_existing().one()
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
                performance.setting.performance_operator_id = f.performance_operator_id.data
                performance.setting.sales_person_id = f.sales_person_id.data
                performance.setting.visible = f.visible.data
                performance.save()

            self.request.session.flash(u'パフォーマンスを保存しました')
            return HTTPFound(location=route_path('performances.show', self.request, performance_id=performance.id))
        else:
            return {
                'form': f,
                'is_copy': False,
                'event': performance.event,
                'route_name': route_name,
                'route_path': self.request.path,
            }

    @view_config(route_name='performances.manycopy', request_method='GET', renderer='altair.app.ticketing:templates/performances/copy.html')
    def manycopy_get(self):
        origin_performance = self.context.performance
        forms = [self.create_origin_performance_form(origin_performance)]

        return {
            'event': origin_performance.event,
            'origin_performance': origin_performance,
            'origin_performance_form': forms[0],
            'forms': forms,
            'cart_helper': cart_helper,
            'route_path': self.request.path,
        }

    @view_config(route_name='performances.manycopy', request_method='POST', renderer='altair.app.ticketing:templates/performances/copy.html')
    def manycopy_post(self):
        # original_perf_id, 1_name, 1_open_on, 1_start_on, 1_end_on, 1_display_order,
        # original_perf_id, 2_name, 2_open_on, 2_start_on, 2_end_on, 2_display_order,
        params = self.request.params.dict_of_lists()
        if len(params) == 0:
            self.request.session.flash(u'コピーするものがありません')
            return HTTPFound(location=route_path('events.index', self.request))

        origin_performance = Performance.get(
            params['id'][0], self.context.organization.id)

        target_total = 0
        if 'name' in params:
            target_total = len(params['name'])

        error_exist = self.validate_manycopy(params, target_total)
        if error_exist:
            forms = []
            if target_total > 0:
                for cnt in range(0, target_total):
                    f = PerformanceManycopyForm()
                    f.id.data = origin_performance.id
                    f.name.data = params['name'][cnt]
                    if params['open_on'][cnt]:
                        f.open_on.data = params['open_on'][cnt]
                    f.start_on.data = params['start_on'][cnt]
                    f.end_on.data = params['end_on'][cnt]
                    f.display_order.data = params['display_order'][cnt]
                    forms.append(f)

            return {
                'event': origin_performance.event,
                'origin_performance': origin_performance,
                'origin_performance_form': self.create_origin_performance_form(origin_performance),
                'forms': forms,
                'cart_helper': cart_helper,
                'route_path': self.request.path,
            }

        code_generator = PerformanceCodeGenerator(self.request)
        for cnt in range(0, target_total):

            new_performance = Performance()

            # POST data
            new_performance.event_id = origin_performance.event_id
            new_performance.name = params['name'][cnt]
            new_performance.name = new_performance.name.replace("&quote;", "\'")
            if params['open_on'][cnt]:
                new_performance.open_on = datetime.datetime.strptime(params['open_on'][cnt], '%Y-%m-%d %H:%M')
            new_performance.start_on = datetime.datetime.strptime(params['start_on'][cnt], '%Y-%m-%d %H:%M')
            if params['end_on'][cnt]:
                new_performance.end_on = datetime.datetime.strptime(params['end_on'][cnt], '%Y-%m-%d %H:%M')
            new_performance.display_order = params['display_order'][cnt]

            # Copy data
            new_performance.code = code_generator.generate(origin_performance.code)
            new_performance.venue_id = origin_performance.venue.id
            new_performance.create_venue_id = origin_performance.venue.id
            new_performance.original_id = origin_performance.id
            new_performance.redirect_url_pc = origin_performance.redirect_url_pc
            new_performance.redirect_url_mobile = origin_performance.redirect_url_mobile
            new_performance.abbreviated_title = origin_performance.abbreviated_title
            new_performance.subtitle = origin_performance.subtitle
            new_performance.subtitle2 = origin_performance.subtitle2
            new_performance.subtitle3 = origin_performance.subtitle3
            new_performance.subtitle4 = origin_performance.subtitle4
            new_performance.note = origin_performance.note
            new_performance.account_id = origin_performance.account_id

            if new_performance.setting is None:
                new_performance.setting = PerformanceSetting()

            new_performance.setting.order_limit = origin_performance.setting.order_limit
            new_performance.setting.entry_limit = origin_performance.setting.entry_limit
            new_performance.setting.max_quantity_per_user = origin_performance.setting.max_quantity_per_user
            new_performance.setting.visible = origin_performance.setting.visible

            if origin_performance.orion is not None:
                new_performance.orion = OrionPerformance.clone(
                    origin_performance.orion, False, ['performance_id'])

            new_performance.save()

            # 抽選の商品を作成する
            copy_lots_between_performance(origin_performance, new_performance)

        self.request.session.flash(u'パフォーマンスをコピーしました')
        return HTTPFound(location=route_path('performances.index', self.request, event_id=origin_performance.event.id))

    def create_origin_performance_form(self, origin_performance):
        f = PerformanceManycopyForm()
        f.id.data = origin_performance.id
        f.name.data = origin_performance.name.replace("\'", "&quote;")
        f.open_on.data = cart_helper.datetime(origin_performance.open_on)
        f.start_on.data = cart_helper.datetime(origin_performance.start_on)
        f.end_on.data = cart_helper.datetime(origin_performance.end_on)
        f.display_order.data = origin_performance.display_order
        return f

    def validate_manycopy(self, params, target_total):
        error_exist = False

        for cnt in range(0, target_total):
            if not params['name'][cnt]:
                self.request.session.flash(u'{}行目の公演名が未入力です。'.format(cnt + 1))
                error_exist = True

            if params['name'][cnt]:
                if params['name'][cnt].count('\t'):
                    self.request.session.flash(u'{}行目の公演名にタブが入っています。'.format(cnt + 1))
                    error_exist = True

            if params['open_on'][cnt]:
                try:
                    datetime.datetime.strptime(
                        params['open_on'][cnt], '%Y-%m-%d %H:%M')
                except ValueError:
                    self.request.session.flash(
                        u'{}行目の開場時刻が不正です。'.format(cnt + 1))
                    error_exist = True

            try:
                start = datetime.datetime.strptime(
                    params['start_on'][cnt], '%Y-%m-%d %H:%M')
                if params['open_on'][cnt]:
                    open = datetime.datetime.strptime(
                        params['open_on'][cnt], '%Y-%m-%d %H:%M')
                    if open > start:
                        self.request.session.flash(
                            u'{}行目の開場時間が、公演開始時刻より後に設定されています。'.format(cnt + 1))
                        error_exist = True
                if params['end_on'][cnt]:
                    end = datetime.datetime.strptime(
                        params['end_on'][cnt], '%Y-%m-%d %H:%M')
                    if end < start:
                        self.request.session.flash(
                            u'{}行目の終演時間が、公演開始時刻より前に設定されています。'.format(cnt + 1))
                        error_exist = True
            except ValueError:
                self.request.session.flash(
                    u'{}行目の公演開始時刻が不正です。'.format(cnt + 1))
                error_exist = True

            try:
                display_order = long(params['display_order'][cnt])
                if -2147483648 > display_order or display_order > 2147483647:
                    self.request.session.flash(
                        u'{}行目の表示順は、-2147483648から、2147483647の間で指定できます。'.format(cnt))
                    error_exist = True
            except ValueError:
                self.request.session.flash(u'{}行目の表示順が不正です。'.format(cnt + 1))
                error_exist = True
        return error_exist

    @view_config(route_name='performances.termcopy', request_method='GET', renderer='altair.app.ticketing:templates/performances/termcopy.html')
    def termcopy_get(self):
        origin_performance = self.context.performance
        form = PerformanceTermForm()

        return {
            'event': origin_performance.event,
            'origin_performance': origin_performance,
            'form': form,
            'cart_helper': cart_helper,
            'route_path': self.request.path,
        }

    @view_config(route_name='performances.termcopy', request_method='POST', renderer='altair.app.ticketing:templates/performances/termcopy.html')
    def termcopy_post(self):
        form = PerformanceTermForm(self.request.POST)
        origin_performance = self.context.performance

        target_total = 0
        if form.start_day.data and form.end_day.data:
            target_total = (form.end_day.data - form.start_day.data).days

        if target_total <= 0:
            return {
                'event': origin_performance.event,
                'origin_performance': origin_performance,
                'form': form,
                'message': u'期間指定が不正です',
                'cart_helper': cart_helper,
                'route_path': self.request.path,
            }

        open_date = None
        end_date = None

        if origin_performance.open_on:
            open_date = form.start_day.data + datetime.timedelta(hours=origin_performance.open_on.hour,
                                                                 minutes=origin_performance.open_on.minute)
        if origin_performance.end_on:
            end_date = form.start_day.data + datetime.timedelta(hours=origin_performance.end_on.hour,
                                                                minutes=origin_performance.end_on.minute)
        start_date = form.start_day.data + datetime.timedelta(hours=origin_performance.start_on.hour,
                                                              minutes=origin_performance.start_on.minute)

        code_generator = PerformanceCodeGenerator(self.request)
        for cnt in range(0, target_total + 1):
            new_performance = Performance()

            if origin_performance.open_on:
                new_performance.open_on = open_date + datetime.timedelta(days=cnt)
            if origin_performance.end_on:
                new_performance.end_on = end_date + datetime.timedelta(days=cnt)
            new_performance.start_on = start_date + datetime.timedelta(days=cnt)

            # Copy data
            new_performance.event_id = origin_performance.event_id
            new_performance.name = origin_performance.name
            new_performance.name = new_performance.name.replace("&quote;", "\'")
            new_performance.display_order = origin_performance.display_order
            new_performance.code = code_generator.generate(origin_performance.code)
            new_performance.venue_id = origin_performance.venue.id
            new_performance.create_venue_id = origin_performance.venue.id
            new_performance.original_id = origin_performance.id
            new_performance.redirect_url_pc = origin_performance.redirect_url_pc
            new_performance.redirect_url_mobile = origin_performance.redirect_url_mobile
            new_performance.abbreviated_title = origin_performance.abbreviated_title
            new_performance.subtitle = origin_performance.subtitle
            new_performance.subtitle2 = origin_performance.subtitle2
            new_performance.subtitle3 = origin_performance.subtitle3
            new_performance.subtitle4 = origin_performance.subtitle4
            new_performance.note = origin_performance.note
            new_performance.account_id = origin_performance.account_id

            if new_performance.setting is None:
                new_performance.setting = PerformanceSetting()

            new_performance.setting.order_limit = origin_performance.setting.order_limit
            new_performance.setting.entry_limit = origin_performance.setting.entry_limit
            new_performance.setting.max_quantity_per_user = origin_performance.setting.max_quantity_per_user
            new_performance.setting.visible = origin_performance.setting.visible

            if origin_performance.orion is not None:
                new_performance.orion = OrionPerformance.clone(
                    origin_performance.orion, False, ['performance_id'])

            new_performance.save()

            # 抽選の商品を作成する
            copy_lots_between_performance(origin_performance, new_performance)

        self.request.session.flash(u'パフォーマンスをコピーしました')
        return HTTPFound(location=route_path('performances.index', self.request, event_id=origin_performance.event.id))

    @view_config(route_name='performances.delete')
    def delete(self):
        performance = self.context.performance
        location = route_path(
            'events.show', self.request, event_id=performance.event_id)
        try:
            performance.delete()
            self.request.session.flash(u'パフォーマンスを削除しました')
        except Exception, e:
            self.request.session.flash(e.message)
            raise HTTPFound(location=route_path(
                'performances.show', self.request, performance_id=performance.id))

        return HTTPFound(location=location)

    @view_config(route_name='performances.open', request_method='GET', renderer='altair.app.ticketing:templates/performances/_form_open.html')
    def open_get(self):
        f = PerformancePublicForm(
            record_to_multidict(self.context.performance))
        f.public.data = 0 if f.public.data == 1 else 1

        return {
            'form': f,
            'performance': self.context.performance,
        }

    @view_config(route_name='performances.open', request_method='POST', renderer='altair.app.ticketing:templates/performances/_form_open.html')
    def open_post(self):
        f = PerformancePublicForm(self.request.POST)

        if f.validate():
            performance = merge_session_with_post(
                self.context.performance, f.data)
            performance.save()

            if performance.public:
                self.request.session.flash(u'パフォーマンスを公開しました')
            else:
                self.request.session.flash(u'パフォーマンスを非公開にしました')
            return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)

        return {
            'form': f,
            'performance': self.context.performance,
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
        mutil = get_mail_utility(
            self.request, self.request.matchdict["mailtype"])
        template = MailInfoTemplate(
            self.request, performance.event.organization, mutil=mutil)
        choice_form = template.as_choice_formclass()()
        formclass = template.as_formclass()
        mailtype = self.request.matchdict["mailtype"]
        form = formclass(
            **(performance.extra_mailinfo.data.get(mailtype, {}) if performance.extra_mailinfo else {}))
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
        mutil = get_mail_utility(
            self.request, self.request.matchdict["mailtype"])
        performance = self.context.performance

        template = MailInfoTemplate(
            self.request, performance.event.organization, mutil=mutil)
        choice_form = template.as_choice_formclass()()
        formclass = template.as_formclass()
        form = formclass(self.request.POST)
        if not form.validate():
            self.request.session.flash(u"入力に誤りがあります。")
        else:
            mailtype = self.request.matchdict["mailtype"]
            mailinfo = mutil.create_or_update_mailinfo(
                self.request, form.as_mailinfo_data(), performance=performance, kind=mailtype)
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


class ResaleForOrionAPIView(BaseView):

    def __init__(self, context, request):
        super(ResaleForOrionAPIView, self).__init__(context, request)
        self.session = get_db_session(request, 'slave')

    def _get_valid_resale_request_action_code(self, action):
        action_code = getattr(ResaleRequestStatus, action, None)
        if not action_code:
            action_code = ResaleRequestStatus.unknown
        return action_code

    @view_config(route_name="performances.resale.send_resale_segment_to_orion",
                 request_method="POST",
                 renderer="json")
    def send_resale_segment_to_orion(self):
        performance_id = int(self.request.params.get('performance_id', None))
        if not performance_id:
            raise HTTPNotFound()
        performance = self.session.query(Performance).get(performance_id)
        resale_segment_id = self.request.params.get('resale_segment_id', None)
        resale_segments = DBSession.query(ResaleSegment).filter(ResaleSegment.performance_id == performance_id)

        if resale_segment_id:
            resale_segments = resale_segments.filter(ResaleSegment.id == resale_segment_id)

        success_list = []
        fail_list = []
        for resale_segment in resale_segments:
            resale_segment.sent_at = datetime.datetime.now()
            try:
                resp = send_resale_segment(self.request, performance, resale_segment)
                if not resp or resp['result'] != u"OK":
                    fail_list.append(resale_segment.id)
                    resale_segment.sent_status = SentStatus.fail
                    logger.info("fail to send resale segment: {0}...".format(resale_segment.id))
                else:
                    success_list.append(resale_segment.id)
                    resale_segment.sent_status = SentStatus.sent
            except Exception as e:
                fail_list.append(resale_segment.id)
                resale_segment.sent_status = SentStatus.fail
                logger.info(
                    "fail to send resale segment(ID: {0}) with the exception: {1} ...".format(
                        resale_segment.id, str(e))
                )

            DBSession.merge(resale_segment)
            DBSession.flush()

        return {
            'success_list': success_list,
            'fail_list': fail_list
        }

    @view_config(route_name="performances.resale.requests.operate",
                 request_method="POST",
                 renderer="json")
    def operate_resale_requests(self):
        resale_request_id = self.request.params.get('resale_request_id', None)
        action = self.request.params.get('action', None)
        if not resale_request_id or not action:
            raise HTTPNotFound

        action_code = self._get_valid_resale_request_action_code(action)
        result = u"OK"
        emsgs = u""
        try:
            resale_request = DBSession.query(ResaleRequest).get(resale_request_id)
            resale_request.status = action_code
            DBSession.merge(resale_request)
            DBSession.flush()
            logger.info("ResaleRequst(ID: {}) was updated as {}".format(resale_request_id, action))
        except Exception as e:
            emsgs = str(e)
            result = u"NG"
            logger.info("ResaleRequst(ID: {}) failed to be updated as {}".format(resale_request_id, action))

        return {'result': result, 'emsgs': emsgs}

    @view_config(route_name="performances.resale.send_resale_request_to_orion",
                 request_method="POST",
                 renderer="json")
    def send_resale_request_to_orion(self):
        resale_request_id = self.request.params.get('resale_request_id', None)
        if not resale_request_id:
            raise HTTPNotFound()

        try:
            resale_request = DBSession.query(ResaleRequest) \
                .filter(ResaleRequest.id == resale_request_id) \
                .filter(ResaleRequest.status != ResaleRequestStatus.unknown) \
                .filter(ResaleRequest.sent_status != SentStatus.sent) \
                .one()
        except Exception:
            raise HTTPNotFound()

        resale_request.sent_at = datetime.datetime.now()
        result = u"OK"
        emsgs = u""
        try:
            resp = send_resale_request(self.request, resale_request)
            if not resp or resp['result'] != u"OK":
                result = u"NG"
                emsgs = u"リセールリクエスト連携は失敗しました。"
                resale_request.sent_status = SentStatus.fail
                logger.info("fail to send resale request(ID: {0}) ...".format(resale_request.id))
            else:
                resale_request.sent_status = SentStatus.sent
        except Exception as e:
            result = u"NG"
            emsgs = u"リセールリクエスト連携は失敗しました。"
            resale_request.sent_status = SentStatus.fail
            logger.info(
                "fail to send resale request(ID: {0}) with the exception: {1} ...".format(
                    resale_request.id, str(e))
            )

        DBSession.merge(resale_request)
        DBSession.flush()

        return {'result': result, 'emsgs': emsgs}

    @view_config(route_name="performances.resale.send_all_resale_request_to_orion",
                 request_method="POST",
                 renderer="json")
    def send_all_resale_request_to_orion(self):
        resale_segment_id = self.request.params.get('resale_segment_id', None)
        if not resale_segment_id:
            raise HTTPNotFound()

        resale_requests = DBSession.query(ResaleRequest) \
            .filter(ResaleRequest.resale_segment_id == resale_segment_id) \
            .filter(ResaleRequest.status.in_([ResaleRequestStatus.sold, ResaleRequestStatus.back])) \
            .filter(ResaleRequest.sent_status != SentStatus.sent)

        if not resale_requests.count():
            raise HTTPNotFound()

        result = u"OK"
        emsgs = u""
        try:
            resale_requests.update({ResaleRequest.sent_at: datetime.datetime.now()}, synchronize_session='fetch')
            resp = send_all_resale_request(self.request, resale_requests.all())
            if not resp or resp['result'] != u"OK":
                logger.info("fail to send the resale request of resale segment(ID: {0}) ...".format(resale_segment_id))
                resale_requests.update({ResaleRequest.sent_status: SentStatus.fail}, synchronize_session='fetch')
                result = u"NG"
                emsgs = u"リセールリクエスト一括連携は失敗しました。"
            else:
                resale_requests.update({ResaleRequest.sent_status: SentStatus.sent}, synchronize_session='fetch')
        except Exception as e:
            logger.info("fail to send the resale request of resale segment(ID: {0}) with the exception: {1}...".format(
                resale_segment_id, str(e))
            )
            resale_requests.update({ResaleRequest.sent_status: SentStatus.fail}, synchronize_session='fetch')
            result = u"NG"
            emsgs = u"リセールリクエスト一括連携は失敗しました。"

        DBSession.flush()

        return {'result': result, 'emsgs': emsgs}