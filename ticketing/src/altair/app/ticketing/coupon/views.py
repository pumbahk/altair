# -*- coding:utf-8 -*-
from pyramid.view import view_defaults
from altair.pyramid_dynamic_renderer import lbr_view_config
from altair.app.ticketing.cart.rendering import selectable_renderer
from pyramid.httpexceptions import HTTPFound
from . import COUPON_COOKIE_NAME
from .api import can_use_coupon, can_use_coupon_order
from datetime import datetime

class CouponErrorView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @lbr_view_config(route_name='coupon.notfound', renderer=selectable_renderer("notfound.html"))
    def notfound(self):
        return dict()

    @lbr_view_config(route_name='coupon.out_term', renderer=selectable_renderer("out_term.html"))
    def out_term(self):
        if self.context.order is None:
            return HTTPFound(location=self.request.route_path('coupon.notfound'))

        return dict(order=self.context.order)


@view_defaults(renderer=selectable_renderer("coupon.html"))
class CouponView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @lbr_view_config(route_name='coupon')
    def show(self):
        if self.context.order is None:
            return HTTPFound(location=self.request.route_path('coupon.notfound'))

        if not self.context.can_use:
            return HTTPFound(location=self.request.route_path(
                'coupon.out_term', reserved_number=self.context.reserved_number.number))

        return dict(
            reserved_number=self.context.reserved_number,
            order=self.context.order,
            term_sales=self.context.is_term_sales,
            coupon_security=self.context.coupon_security
            )

    @lbr_view_config(
        route_name='coupon.admission', request_method='GET')
    def admission(self):
        if self.context.order is None:
            return HTTPFound(location=self.request.route_path('coupon.notfound'))

        if not self.context.can_use:
            return HTTPFound(location=self.request.route_path(
                'coupon.out_term', reserved_number=self.context.reserved_number.number))

        return dict(
            reserved_number=self.context.reserved_number,
            order=self.context.order,
            term_sales=self.context.is_term_sales,
            coupon_security=self.context.coupon_security
            )

    @lbr_view_config(
        route_name='coupon.admission', request_method='POST')
    def admission_post(self):
        if self.context.order is None:
            return HTTPFound(location=self.request.route_path('coupon.notfound'))

        if not self.context.can_use:
            return HTTPFound(location=self.request.route_path(
                'coupon.out_term', reserved_number=self.context.reserved_number.number))

        self.context.use_coupon()

        # 確認画面を出すかどうか
        if self.request.POST.get('disp_dialog', None):
            self.request.response.set_cookie(COUPON_COOKIE_NAME, str(datetime.now()))

        return dict(
            reserved_number=self.context.reserved_number,
            order=self.context.order,
            term_sales=self.context.is_term_sales,
            coupon_security=self.context.coupon_security
            )

    @lbr_view_config(
        route_name='coupon.order_admission', request_method='GET')
    def order_admission(self):
        if self.context.order is None:
            return HTTPFound(location=self.request.route_path('coupon.notfound'))

        if not self.context.can_use:
            return HTTPFound(location=self.request.route_path(
                'coupon.out_term', reserved_number=self.context.reserved_number.number))

        return dict(
            reserved_number=self.context.reserved_number,
            order=self.context.order,
            term_sales=self.context.is_term_sales,
            coupon_security=self.context.coupon_security
            )

    @lbr_view_config(
        route_name='coupon.order_admission', request_method='POST')
    def order_admission_post(self):
        if self.context.order is None:
            return HTTPFound(location=self.request.route_path('coupon.notfound'))

        if not self.context.can_use:
            return HTTPFound(location=self.request.route_path(
                'coupon.out_term', reserved_number=self.context.reserved_number.number))

        self.context.use_all_coupon()

        return dict(
            reserved_number=self.context.reserved_number,
            order=self.context.order,
            term_sales=self.context.is_term_sales,
            coupon_security=self.context.coupon_security
            )

    @lbr_view_config(
        route_name='coupon.check_can_use', request_method="GET", renderer='json')
    def check_can_use(self):
        return can_use_coupon(self.request, self.request.matchdict.get('token_id', None))

    @lbr_view_config(
        route_name='coupon.check_can_use_order', request_method="GET", renderer='json')
    def check_can_use_order(self):
        if self.context.order is None:
            return False
        return can_use_coupon_order(self.request, self.context.order)
