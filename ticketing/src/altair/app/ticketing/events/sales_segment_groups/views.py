# -*- coding: utf-8 -*-

import json
from datetime import datetime

import webhelpers.paginate as paginate
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPBadRequest
from pyramid.renderers import render_to_response
from pyramid.url import route_path

from altair.app.ticketing.models import merge_session_with_post, record_to_multidict
from altair.app.ticketing.views import BaseView
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.core.models import Event, SalesSegment, SalesSegmentGroup, Product
from altair.app.ticketing.events.payment_delivery_method_pairs.forms import PaymentDeliveryMethodPairForm
from altair.app.ticketing.events.sales_segment_groups.forms import SalesSegmentGroupForm, MemberGroupToSalesSegmentForm
from altair.app.ticketing.events.sales_segments.forms import SalesSegmentForm
from altair.app.ticketing.memberships.forms import MemberGroupForm
from altair.app.ticketing.users.models import MemberGroup, Membership
from .resources import SalesSegmentGroupUpdate

@view_defaults(decorator=with_bootstrap, permission='event_editor')
class SalesSegmentGroups(BaseView):

    @view_config(route_name='sales_segment_groups.index', renderer='altair.app.ticketing:templates/sales_segment_groups/index.html')
    def index(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id, organization_id=self.context.user.organization_id)

        sort = self.request.GET.get('sort', 'SalesSegmentGroup.id')
        direction = self.request.GET.get('direction', 'asc')
        if direction not in ['asc', 'desc']:
            direction = 'asc'

        conditions = {
            'event_id':event.id
        }
        query = SalesSegmentGroup.filter_by(**conditions)
        query = query.order_by(sort + ' ' + direction)

        sales_segment_groups = paginate.Page(
            query,
            page=int(self.request.params.get('page', 0)),
            items_per_page=20,
            url=paginate.PageURL_WebOb(self.request)
        )

        return {
            'form_sales_segment_group':SalesSegmentGroupForm(event_id=event_id),
            'sales_segment_groups':sales_segment_groups,
            'event':event,
        }

    @view_config(route_name='sales_segment_groups.show', renderer='altair.app.ticketing:templates/sales_segment_groups/show.html')
    def show(self):
        sales_segment_group_id = int(self.request.matchdict.get('sales_segment_group_id', 0))
        sales_segment_group = SalesSegmentGroup.get(sales_segment_group_id, self.context.user.organization_id)
        if sales_segment_group is None:
            return HTTPNotFound('sales_segment_group id %d is not found' % sales_segment_group_id)

        member_groups = sales_segment_group.membergroups
        form_ss = SalesSegmentGroupForm(obj=sales_segment_group, event_id=sales_segment_group.event_id)
        form_s = SalesSegmentForm(performances=sales_segment_group.event.performances, sales_segment_groups=[sales_segment_group])

        return {
            'form_s':form_s,
            'form_ss':form_ss,
            'member_groups': member_groups, 
            'sales_segment_group':sales_segment_group,
        }

    @view_config(route_name='sales_segment_groups.new', request_method='GET', renderer='altair.app.ticketing:templates/sales_segment_groups/_form.html', xhr=True)
    def new_xhr(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id, organization_id=self.context.user.organization_id)
        if not event:
            raise HTTPBadRequest(body=json.dumps({
                'message':u'イベントが存在しません',
            }))

        f = SalesSegmentGroupForm(None, event_id=event_id, new_form=True)

        return {
            'form': f,
            'action': self.request.path,
            }

    @view_config(route_name='sales_segment_groups.new', request_method='POST', renderer='altair.app.ticketing:templates/sales_segment_groups/_form.html', xhr=True)
    def new_post(self):
        event_id = int(self.request.POST.get('event_id', 0))
        event = Event.get(event_id, organization_id=self.context.user.organization_id)
        if not event:
            return HTTPNotFound('event id %d is not found' % event_id)

        f = SalesSegmentGroupForm(self.request.POST, event_id=event_id, new_form=True)
        if f.validate():
            if f.start_at.data is None:
                f.start_at.data = datetime.now() 
            if f.end_at.data is None:
                f.end_at.data = datetime.now()
            sales_segment_group = merge_session_with_post(SalesSegmentGroup(), f.data)
            sales_segment_group.organization = self.context.user.organization
            sales_segment_group.save()

            self.request.session.flash(u'販売区分グループを保存しました')
            return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)
        else:
            return {
                'form':f,
            }

    @view_config(route_name='sales_segment_groups.copy', request_method='GET', renderer='altair.app.ticketing:templates/sales_segment_groups/_form.html', xhr=True)
    @view_config(route_name='sales_segment_groups.edit', request_method='GET', renderer='altair.app.ticketing:templates/sales_segment_groups/_form.html', xhr=True)
    def edit_xhr(self):
        sales_segment_group_id = int(self.request.matchdict.get('sales_segment_group_id', 0))
        sales_segment_group = SalesSegmentGroup.get(sales_segment_group_id, self.context.user.organization_id)
        if sales_segment_group is None:
            return HTTPNotFound('sales_segment_group id %d is not found' % sales_segment_group_id)

        return {
            'form': SalesSegmentGroupForm(record_to_multidict(sales_segment_group), event_id=sales_segment_group.event_id),
            'action': self.request.path,
            }

    def _edit_post(self):
        sales_segment_group_id = int(self.request.matchdict.get('sales_segment_group_id', 0))
        sales_segment_group = SalesSegmentGroup.get(sales_segment_group_id, self.context.user.organization_id)
        if sales_segment_group is None:
            return HTTPNotFound('sales_segment_group id %d is not found' % sales_segment_group_id)

        f = SalesSegmentGroupForm(self.request.POST, event_id=sales_segment_group.event_id)
        if not f.validate():
            return f
        if self.request.matched_route.name == 'sales_segment_groups.copy':
            with_pdmp = bool(f.copy_payment_delivery_method_pairs.data)
            id_map = SalesSegmentGroup.create_from_template(sales_segment_group, with_payment_delivery_method_pairs=with_pdmp)
            f.id.data = id_map[sales_segment_group_id]
            new_sales_segment_group = merge_session_with_post(SalesSegmentGroup.get(f.id.data), f.data)
            new_sales_segment_group.save()

            for ss in sales_segment_group.sales_segments:
                id_map = SalesSegment.create_from_template(ss, sales_segment_group_id=new_sales_segment_group.id)
                if bool(f.copy_products.data):
                    for product in ss.products:
                        Product.create_from_template(template=product, with_product_items=True, stock_holder_id=f.copy_to_stock_holder.data, sales_segment=id_map)

            new_sales_segment_group.sync_member_group_to_children()
            
        else:
            sales_segment_group = merge_session_with_post(sales_segment_group, f.data)
            sales_segment_group.save()

            sales_segment_group.sync_member_group_to_children()
            SalesSegmentGroupUpdate(sales_segment_group).update(
                sales_segment_group.sales_segments)

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
        sales_segment_group_id = int(self.request.matchdict.get('sales_segment_group_id', 0))
        sales_segment_group = SalesSegmentGroup.get(sales_segment_group_id, self.context.user.organization_id)
        if sales_segment_group is None:
            return HTTPNotFound('sales_segment_group id %d is not found' % sales_segment_group_id)

        location = route_path('sales_segment_groups.index', self.request, event_id=sales_segment_group.event_id)
        try:
            sales_segment_group.delete()
            self.request.session.flash(u'販売区分を削除しました')
        except Exception, e:
            self.request.session.flash(e.message)
            raise HTTPFound(location=location)

        return HTTPFound(location=location)

    @view_config(route_name="sales_segment_groups.bind_membergroup",
                 renderer='altair.app.ticketing:templates/sales_segment_groups/bind_membergroup.html', request_method="GET")
    def bind_membergroup_get(self):
        sales_segment_group_id = int(self.request.matchdict.get('sales_segment_group_id', 0))
        sales_segment_group = SalesSegmentGroup.get(sales_segment_group_id, self.context.user.organization_id)
        if sales_segment_group is None:
            return HTTPNotFound('sales_segment_group id %d is not found' % sales_segment_group_id)
        
        redirect_to = self.request.route_path("sales_segment_groups.show",  sales_segment_group_id=sales_segment_group_id)
        membergroups = MemberGroup.query.filter(MemberGroup.membership_id==Membership.id, Membership.organization_id==self.context.user.organization_id)
        form = MemberGroupToSalesSegmentForm(obj=sales_segment_group, membergroups=membergroups)
        return {"form": form,
                "membergroups": sales_segment_group.membergroups,
                'form_mg': MemberGroupForm(),
                'form_ss': SalesSegmentGroupForm(),
                "sales_segment_group":sales_segment_group,
                "redirect_to": redirect_to,
                "sales_segment_group_id": sales_segment_group_id}

    @view_config(route_name="sales_segment_groups.bind_membergroup",
                 renderer='altair.app.ticketing:templates/sales_segment_groups/bind_membergroup.html', request_method="POST")
    def bind_membergroup_post(self):
        sales_segment_group_id = int(self.request.matchdict.get('sales_segment_group_id', 0))
        sales_segment_group = SalesSegmentGroup.get(sales_segment_group_id, self.context.user.organization_id)
        if sales_segment_group is None:
            return HTTPNotFound('sales_segment_group id %d is not found' % sales_segment_group_id)
        
        candidates_membergroups = MemberGroup.query
        will_bounds = candidates_membergroups.filter(MemberGroup.id.in_(self.request.POST.getall("membergroups")))

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

