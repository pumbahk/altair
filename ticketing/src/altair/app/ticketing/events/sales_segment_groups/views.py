# -*- coding: utf-8 -*-

import json
from datetime import datetime
import logging

import webhelpers.paginate as paginate
from sqlalchemy import sql
from sqlalchemy.orm.util import class_mapper
from sqlalchemy.orm.attributes import QueryableAttribute
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPBadRequest
from pyramid.renderers import render_to_response
from pyramid.url import route_path

from altair.sqla import new_comparator

from altair.app.ticketing.models import merge_session_with_post, record_to_multidict
from altair.app.ticketing.views import BaseView
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.core.models import Event, SalesSegment, SalesSegmentGroup, SalesSegmentGroupSetting, Product
from altair.app.ticketing.events.payment_delivery_method_pairs.forms import PaymentDeliveryMethodPairForm
from altair.app.ticketing.events.sales_segments.forms import SalesSegmentForm
from altair.app.ticketing.events.sales_segments.views import SalesSegmentViewHelperMixin
from altair.app.ticketing.memberships.forms import MemberGroupForm
from altair.app.ticketing.users.models import MemberGroup, Membership
from altair.app.ticketing.events.sales_segments.resources import SalesSegmentAccessor

from .forms import SalesSegmentGroupForm, MemberGroupToSalesSegmentForm

logger = logging.getLogger(__name__)

@view_defaults(decorator=with_bootstrap, permission='event_editor')
class SalesSegmentGroups(BaseView, SalesSegmentViewHelperMixin):
    @view_config(route_name='sales_segment_groups.index', renderer='altair.app.ticketing:templates/sales_segment_groups/index.html')
    def index(self):
        sort_column = self.request.GET.get('sort', 'id')
        try:
            mapper = class_mapper(SalesSegmentGroup)
            prop = mapper.get_property(sort_column)
            sort = new_comparator(prop,  mapper)
        except:
            sort = None
        direction = { 'asc': sql.asc, 'desc': sql.desc }.get(
            self.request.GET.get('direction'),
            sql.asc
            )

        conditions = {
            'event_id': self.context.event.id
        }
        query = SalesSegmentGroup.filter_by(**conditions)
        if sort is not None:
            query = query.order_by(direction(sort))

        sales_segment_groups = paginate.Page(
            query,
            page=int(self.request.params.get('page', 0)),
            items_per_page=20,
            url=paginate.PageURL_WebOb(self.request)
        )

        return {
            'form_sales_segment_group':SalesSegmentGroupForm(context=self.context),
            'sales_segment_groups':sales_segment_groups,
            'event': self.context.event,
        }

    @view_config(route_name='sales_segment_groups.show', renderer='altair.app.ticketing:templates/sales_segment_groups/show.html')
    def show(self):
        return {
            'form_s': SalesSegmentForm(context=self.context),
            'member_groups': self.context.sales_segment_group.membergroups, 
            'sales_segment_group':self.context.sales_segment_group,
            }

    @view_config(route_name='sales_segment_groups.new', request_method='GET', renderer='altair.app.ticketing:templates/sales_segment_groups/_form.html', xhr=True)
    def new_xhr(self):
        return {
            'form': SalesSegmentGroupForm(None, context=self.context, new_form=True),
            'action': self.request.path,
            }

    @view_config(route_name='sales_segment_groups.new', request_method='POST', renderer='altair.app.ticketing:templates/sales_segment_groups/_form.html', xhr=True)
    def new_post(self):
        f = SalesSegmentGroupForm(self.request.POST, context=self.context, new_form=True)
        if f.validate():
            sales_segment_group = merge_session_with_post(
                SalesSegmentGroup(
                    organization=self.context.organization,
                    setting=SalesSegmentGroupSetting(
                        order_limit=f.order_limit.data,
                        max_quantity_per_user=f.max_quantity_per_user.data,
                        disp_orderreview=True,
                        disp_agreement=f.disp_agreement.data,
                        agreement_body=f.agreement_body.data,
                        )
                    ),
                f.data,
                excludes=SalesSegmentAccessor.setting_attributes
                )
            sales_segment_group.save()
            accessor = SalesSegmentAccessor()
            for performance in self.context.event.performances:
                accessor.create_sales_segment_for_performance(sales_segment_group, performance)
            self.request.session.flash(u'販売区分グループを保存しました')
            return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)
        else:
            return {
                'form':f,
                'action': self.request.path,
                }

    @view_config(route_name='sales_segment_groups.copy', request_method='GET', renderer='altair.app.ticketing:templates/sales_segment_groups/_form.html', xhr=True)
    @view_config(route_name='sales_segment_groups.edit', request_method='GET', renderer='altair.app.ticketing:templates/sales_segment_groups/_form.html', xhr=True)
    def edit_xhr(self):
        sales_segment_group = self.context.sales_segment_group
        form = SalesSegmentGroupForm(obj=sales_segment_group, context=self.context)
        for k in SalesSegmentAccessor.setting_attributes:
            getattr(form, k).data = getattr(sales_segment_group.setting, k)
        return {
            'form': form,
            'action': self.request.path,
            }

    # TODO: copyのときに、コピー先の販売区分グループの詳細画面に遷移しない
    def _edit_post(self):
        f = SalesSegmentGroupForm(self.request.POST, context=self.context)
        if not f.validate():
            return f
        sales_segment_group = self.context.sales_segment_group
        if self.request.matched_route.name == 'sales_segment_groups.copy':
            with_pdmp = bool(f.copy_payment_delivery_method_pairs.data)
            try:
                # id_map は { テンプレートのid: 新しいSalesSegmentGroupのid }
                id_map = SalesSegmentGroup.create_from_template(sales_segment_group, with_payment_delivery_method_pairs=with_pdmp)
            except Exception, exception:
                self.request.session.flash(exception.message.decode('utf-8'))
                return None
            f.id.data = id_map[self.context.sales_segment_group.id]
            # XXX: なぜこれを取り直す必要が? create_from_template がそのまま実体を返せば済む話では?
            new_sales_segment_group = SalesSegmentGroup.query.filter_by(id=f.id.data).one()
            new_sales_segment_group = merge_session_with_post(new_sales_segment_group, f.data, excludes=SalesSegmentAccessor.setting_attributes)
            new_sales_segment_group.setting.order_limit = f.order_limit.data
            new_sales_segment_group.setting.max_quantity_per_user = f.max_quantity_per_user.data
            new_sales_segment_group.setting.disp_orderreview = f.disp_orderreview.data
            new_sales_segment_group.setting.disp_agreement = f.disp_agreement.data
            new_sales_segment_group.setting.agreement_body = f.agreement_body.data
            new_sales_segment_group.setting.display_seat_no = f.display_seat_no.data
            new_sales_segment_group.setting.sales_counter_selectable = f.sales_counter_selectable.data
            new_sales_segment_group.setting.extra_form_fields = f.extra_form_fields.data
            new_sales_segment_group.save()

            accessor = SalesSegmentAccessor()
            for sales_segment in sales_segment_group.sales_segments:
                id_map = SalesSegment.create_from_template(
                    sales_segment,
                    sales_segment_group_id=new_sales_segment_group.id
                    )
                if bool(f.copy_products.data):
                    for product in sales_segment.products:
                        Product.create_from_template(
                            template=product,
                            with_product_items=True,
                            stock_holder_id=f.copy_to_stock_holder.data,
                            sales_segment=id_map
                            )
                # id_map は { テンプレートのid: 新しいSalesSegmentGroupのid }
                # XXX: なぜこれを取り直す必要が? create_from_template がそのまま実体を返せば済む話では?
                new_sales_segment = SalesSegment.query.filter_by(id=id_map[sales_segment.id]).one()
                accessor.update_sales_segment(new_sales_segment)

            new_sales_segment_group.sync_member_group_to_children()
            
        else:
            sales_segment_group = merge_session_with_post(sales_segment_group, f.data, excludes=SalesSegmentAccessor.setting_attributes)
            if sales_segment_group.setting is None:
                sales_segment_group.setting = SalesSegmentGroupSetting()
            sales_segment_group.setting.order_limit = f.order_limit.data
            sales_segment_group.setting.max_quantity_per_user = f.max_quantity_per_user.data
            sales_segment_group.setting.disp_orderreview = f.disp_orderreview.data
            sales_segment_group.setting.disp_agreement = f.disp_agreement.data
            sales_segment_group.setting.agreement_body = f.agreement_body.data
            sales_segment_group.setting.display_seat_no = f.display_seat_no.data
            sales_segment_group.setting.sales_counter_selectable = f.sales_counter_selectable.data
            sales_segment_group.setting.extra_form_fields = f.extra_form_fields.data
            sales_segment_group.save()

            sales_segment_group.sync_member_group_to_children()
            accessor = SalesSegmentAccessor()
            for sales_segment in sales_segment_group.sales_segments:
                logger.info('propagating changes to sales_segment(id=%ld)' % sales_segment.id)
                accessor.update_sales_segment(sales_segment)

        self.request.session.flash(u'販売区分グループを保存しました')
        return None

    @view_config(route_name='sales_segment_groups.copy', request_method='POST', renderer='altair.app.ticketing:templates/sales_segment_groups/_form.html')
    @view_config(route_name='sales_segment_groups.edit', request_method='POST', renderer='altair.app.ticketing:templates/sales_segment_groups/_form.html')
    def edit_post_xhr(self):
        f = self._edit_post()
        if f is None:
            return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)
        else:
            return {
                'form': f,
                'action': self.request.path,
                }

    @view_config(route_name='sales_segment_groups.delete')
    def delete(self):
        location = route_path('sales_segment_groups.index', self.request, event_id=self.context.sales_segment_group.event_id)

        if self.context.sales_segment_group.sales_segments:
            self.request.session.flash(u"この販売区分グループは"
                                       u"販売区分を持っているため"
                                       u"削除できません")
            return HTTPFound(location=location)
        try:
            self.context.sales_segment_group.delete()
            self.request.session.flash(u'販売区分グループを削除しました')
        except Exception, e:
            self.request.session.flash(e.message)
            raise HTTPFound(location=location)

        return HTTPFound(location=location)

    @view_config(route_name="sales_segment_groups.bind_membergroup",
                 renderer='altair.app.ticketing:templates/sales_segment_groups/bind_membergroup.html', request_method="GET")
    def bind_membergroup_get(self):
        sales_segment_group = self.context.sales_segment_group
        redirect_to = self.request.route_path("sales_segment_groups.show",  sales_segment_group_id=sales_segment_group.id)
        membergroups = MemberGroup.query.filter(MemberGroup.membership_id==Membership.id, Membership.organization_id==self.context.user.organization_id)
        form = MemberGroupToSalesSegmentForm(obj=sales_segment_group, membergroups=membergroups)
        return {
            'form': form,
            'membergroups': sales_segment_group.membergroups,
            'form_mg': MemberGroupForm(),
            'sales_segment_group':sales_segment_group,
            'redirect_to': redirect_to,
            'sales_segment_group_id': sales_segment_group.id
            }

    @view_config(route_name="sales_segment_groups.bind_membergroup",
                 renderer='altair.app.ticketing:templates/sales_segment_groups/bind_membergroup.html', request_method="POST")
    def bind_membergroup_post(self):
        sales_segment_group = self.context.sales_segment_group
        candidates_membergroups = MemberGroup.query
        will_bounds = candidates_membergroups.filter(MemberGroup.id.in_(self.request.POST.getall("membergroups")))
        membership = Membership.query.join(MemberGroup, MemberGroup.membership_id == Membership.id).\
            filter(MemberGroup.id.in_(self.request.POST.getall("membergroups"))).all()

        if membership:
            if len(membership) > 1:
                self.request.session.flash(u'会員種別が同じものしか同時に登録できません。')
                return HTTPFound(self.request.POST["redirect_to"])

        will_removes = {}
        for mg in sales_segment_group.membergroups:
            will_removes[unicode(mg.id)] = mg

        for mg in will_bounds:
            if unicode(mg.id) in will_removes:
                del will_removes[unicode(mg.id)]
            else:
                sales_segment_group.membergroups.append(mg)

        for mg in will_removes.values():
            sales_segment_group.membergroups.remove(mg)

        sales_segment_group.save()
        sales_segment_group.sync_member_group_to_children()

        self.request.session.flash(u'membergroupの結びつき変更しました')
        return HTTPFound(self.request.POST["redirect_to"])

