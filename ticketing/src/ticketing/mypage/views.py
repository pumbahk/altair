# -*- coding:utf-8 -*-
import logging
from pyramid.view import view_config

from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from ticketing.orders.models import Order, OrderedProduct, OrderedProductItem
from ticketing.cart.rakuten_auth.api import authenticated_user, forget
from ticketing.cart import helpers as h
from .helpers import make_order_data

import webhelpers.paginate as paginate

import sqlahelper

DBSession = sqlahelper.get_session()

logger = logging.getLogger(__name__)

class MyPageView(object):

    def __init__(self, request):
        self.request = request

    @view_config(route_name='mypage.index', renderer='mypage/index.html', xhr=False, permission="view")
    def index(self):

        openid = authenticated_user(self.request)
        user = h.get_or_create_user(self.request, openid['clamed_id'])

        q = self.request.POST.get('q')
        sort = self.request.GET.get('sort', 'Order.id')
        direction = self.request.GET.get('direction', 'asc')
        if direction not in ['asc', 'desc']:
            direction = 'asc'

        query = Order.filter(Order.user_id == user.id)
        if q:
            print ">>>>>>>>>>>>>>"
            print q
            print ">>>>>>>>>>>>>>"
            query = Order.filter(Order.order_no == q)
        query = query.order_by(sort + ' ' + direction)

        # search condition
        if self.request.method == 'POST':
            condition = self.request.POST.get('order_number')
            if condition:
                query = query.filter(Order.order_no==condition)

        orders = paginate.Page(
            query,
            page=int(self.request.params.get('page', 0)),
            items_per_page=20,
            url=paginate.PageURL_WebOb(self.request)
        )

        print user.user_profile
        return dict(
            q = q,
            user = user.user_profile,
            orders = orders
        )

    @view_config(route_name='mypage.logout', renderer='mypage/logout.html', xhr=False, permission="view")
    def logout(self):
        """
        """
        headers = forget(self.request)
        return HTTPFound(location = '/',
                         headers = headers)



    @view_config(route_name='mypage.order', renderer='mypage/order.html', xhr=False, permission="view")
    def order(self):

        openid = authenticated_user(self.request)
        user = h.get_or_create_user(self.request, openid['clamed_id'])
        order_id = int(self.request.matchdict.get('order_id', 0))

        from sqlalchemy.orm.exc import NoResultFound
        order = None
        try:
            order = Order.filter_by(id = order_id , user_id = user.id).one()
        except NoResultFound, e:
            raise HTTPNotFound()

        import locale
        locale.setlocale(locale.LC_ALL, 'ja_JP')
        return dict(
            order = make_order_data(order),
            user = user.user_profile
        )
