# -*- coding:utf-8 -*-
from datetime import datetime

from altair.app.ticketing.cart.rendering import selectable_renderer
from altair.pyramid_dynamic_renderer import lbr_view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_defaults

from . import PASSPORT_COOKIE_NAME
from .api import can_use_passport, can_use_passport_order


class PassportErrorView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @lbr_view_config(route_name='passport.notfound', renderer=selectable_renderer("notfound.html"))
    def notfound(self):
        return dict()


@view_defaults(renderer=selectable_renderer("passport.html"))
class PassportView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @lbr_view_config(route_name='passport')
    def show(self):
        if self.context.order is None:
            return HTTPFound(location=self.request.route_path('passport.notfound'))

        return dict(
            reserved_number=self.context.reserved_number,
            order=self.context.order,
            passport_security=self.context.passport_security
        )

    @lbr_view_config(
        route_name='passport.admission', request_method='GET')
    def admission(self):
        if self.context.order is None:
            return HTTPFound(location=self.request.route_path('passport.notfound'))

        return dict(
            reserved_number=self.context.reserved_number,
            order=self.context.order,
            passport_security=self.context.passport_security
        )

    @lbr_view_config(
        route_name='passport.admission', request_method='POST')
    def admission_post(self):
        if self.context.order is None:
            return HTTPFound(location=self.request.route_path('passport.notfound'))

        self.context.use_passport()

        # 確認画面を出すかどうか
        if self.request.POST.get('disp_dialog', None):
            self.request.response.set_cookie(PASSPORT_COOKIE_NAME, str(datetime.now()))

        return dict(
            reserved_number=self.context.reserved_number,
            order=self.context.order,
            passport_security=self.context.passport_security
        )

    @lbr_view_config(
        route_name='passport.order_admission', request_method='GET')
    def order_admission(self):
        if self.context.order is None:
            return HTTPFound(location=self.request.route_path('passport.notfound'))

        if not self.context.can_use:
            return HTTPFound(location=self.request.route_path(
                'passport.out_term', reserved_number=self.context.reserved_number.number))

        return dict(
            reserved_number=self.context.reserved_number,
            order=self.context.order,
            passport_security=self.context.passport_security
        )

    @lbr_view_config(
        route_name='passport.order_admission', request_method='POST')
    def order_admission_post(self):
        if self.context.order is None:
            return HTTPFound(location=self.request.route_path('passport.notfound'))

        self.context.use_all_passport()

        return dict(
            reserved_number=self.context.reserved_number,
            order=self.context.order,
            passport_security=self.context.passport_security
        )

    @lbr_view_config(
        route_name='passport.check_can_use', request_method="GET", renderer='json')
    def check_can_use(self):
        passport_user = self.context.passport_user
        return can_use_passport(self.request, passport_user)

    @lbr_view_config(
        route_name='passport.check_can_use_order', request_method="GET", renderer='json')
    def check_can_use_order(self):
        if self.context.order is None:
            return False
        return can_use_passport_order(self.request, self.context.order)
