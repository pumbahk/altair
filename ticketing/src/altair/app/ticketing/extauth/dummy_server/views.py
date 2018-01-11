# encoding: UTF-8

import json

import logging
from datetime import datetime
from pyramid.view import view_defaults, view_config
from pyramid.decorator import reify
from sqlalchemy import orm
from sqlalchemy.orm.exc import NoResultFound
import sqlalchemy as sa
from pyramid.response import Response
from .models import EaglesUser, EaglesMembership, VisselUser, VisselMembership, EaglesCoupon
from .interfaces import IRequestHandler
from .exceptions import BadRequestError

logger = logging.getLogger(__name__)


@view_defaults(renderer='json')
class ExtauthCheckMembershipAPI(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_request_handler(self, type):
        return self.request.registry.queryUtility(IRequestHandler, name=type)

    @view_config(route_name='extauth_dummy.check_memberships', context=orm.exc.NoResultFound)
    def no_result_found(self):
        handler = self.get_request_handler('check_memberships')
        response = handler.build_response(
            self.request,
            flavor='json',
            successful=True,
            value=None
            )
        response.status = 200
        return response

    @view_config(route_name='extauth_dummy.check_memberships', context=BadRequestError)
    def bad_request(self):
        handler = self.get_request_handler('check_memberships')
        response = handler.build_response(
            self.request,
            flavor='json',
            successful=False,
            value=self.context.message
            )
        response.status = 400
        return response

    def eagles_user_profile(self):
        handler = self.get_request_handler('check_memberships')
        params = handler.handle_request(self.request)
        openid_claimed_id = params['openid_claimed_id']
        include_permanent_memberships = params['include_permanent_memberships']
        user = self.request.sa_session.query(EaglesUser) \
            .filter(EaglesUser.openid_claimed_id == openid_claimed_id) \
            .one()
        cond = sa.and_(
            (EaglesMembership.valid_since == None) \
            | (EaglesMembership.valid_since <= datetime(params['start_year'], 1, 1)),
            (EaglesMembership.expire_at == None) \
            | (EaglesMembership.expire_at >= datetime(params['end_year'] + 1, 1, 1))
            )
        if not include_permanent_memberships:
            cond = sa.and_(
                cond,
                (EaglesMembership.valid_since != None) | (EaglesMembership.expire_at != None)
                )
        memberships = self.request.sa_session.query(EaglesMembership) \
            .filter(EaglesMembership.user_id == user.id) \
            .filter(cond) \
            .all()
        return handler.build_response(
            self.request,
            flavor='json',
            successful=True,
            value=memberships
            )

    def vissel_user_profile(self):
        handler = self.get_request_handler('check_memberships')
        params = handler.handle_request(self.request)
        openid_claimed_id = params['openid_claimed_id']
        include_permanent_memberships = params['include_permanent_memberships']
        user = self.request.sa_session.query(VisselUser) \
            .filter(VisselUser.openid_claimed_id == openid_claimed_id) \
            .one()
        cond = sa.and_(
            (VisselMembership.valid_since == None) \
            | (VisselMembership.valid_since <= datetime(params['start_year'], 1, 1)),
            (VisselMembership.expire_at == None) \
            | (VisselMembership.expire_at >= datetime(params['end_year'] + 1, 1, 1))
            )
        if not include_permanent_memberships:
            cond = sa.and_(
                cond,
                (VisselMembership.valid_since != None) | (VisselMembership.expire_at != None)
                )
        memberships = self.request.sa_session.query(VisselMembership) \
            .filter(VisselMembership.user_id == user.id) \
            .filter(cond) \
            .all()
        return handler.build_response(
            self.request,
            flavor='json',
            successful=True,
            value=memberships
            )

    @view_config(route_name='extauth_dummy.check_memberships')
    def user_profile(self):
        # viewをorgごとに分離できると良かったがなかなか難しかったので
        # client_nameで切り分けてmethodを呼び分ける
        port = self.request.environ['SERVER_PORT']
        if self.request.params['client_name'] == 'eaglesticket':
            return self.eagles_user_profile()
        elif self.request.params['client_name'] == 'visselticket':
            return self.vissel_user_profile()


@view_defaults(renderer='json')
class EaglesDiscountCodeAPI(object):
    # TODO ハッシュのチェック。

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(route_name='extauth_dummy.confirm_coupon_status')
    def eagles_confirm_coupon_status(self):
        # TODO fc_member_idのチェック。
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%s")
        client_name = self.request.POST['client_name']
        token = self.request.POST['token']
        confirmation_condition = json.loads(self.request.POST['confirmation_condition'])

        resp_data = {
            'status': 'OK',
            'timestamp': timestamp,
            'usage_type': '1010',
            'fc_member_id': confirmation_condition['fc_member_id'],
            'coupons': []
        }

        for req_coupon in confirmation_condition['coupons']:
            try:
                coupon = self.request.sa_session.query(EaglesCoupon) \
                    .filter(EaglesCoupon.code == req_coupon['coupon_cd']) \
                    .one()

                add_dict = {
                    'coupon_cd': coupon.code,
                    'coupon_type': '1010',
                    'name': coupon.name,
                    'available_flg': str(coupon.available_flg),
                    'reason_cd': '1010' if coupon.available_flg else '1030'
                }

            except NoResultFound:
                add_dict = {
                    'coupon_cd': req_coupon['coupon_cd'],
                    'coupon_type': '',
                    'name': '',
                    'available_flg': '0',
                    'reason_cd': '2010'
                }

            resp_data['coupons'].append(add_dict)

        return Response(
            content_type='application/json',
            charset='utf-8',
            text=json.dumps(resp_data, ensure_ascii=False)
        )

    @view_config(route_name='extauth_dummy.use_coupon')
    def eagles_use_coupon(self):
        # TODO fc_member_idのチェック。
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%s")
        client_name = self.request.POST['client_name']
        token = self.request.POST['token']
        usage_coupons = json.loads(self.request.POST['usage_coupons'])

        resp_data = {
            'status': 'OK',
            'timestamp': timestamp,
            'usage_type': '1010',
            'fc_member_id': usage_coupons['fc_member_id'],
            'use_result': '',
            'coupons': []
        }

        for req_coupon in usage_coupons['coupons']:
            try:
                coupon = self.request.sa_session.query(EaglesCoupon).filter(
                    EaglesCoupon.code == req_coupon['coupon_cd']).one()

                if coupon.available_flg == 1:
                    coupon.available_flg = 0
                    self.request.sa_session.commit()
                    reason_cd = '1010'  # 使用した
                else:
                    reason_cd = '1030'  # すでに使用済みで利用できなかった

                add_dict = {
                    'coupon_cd': coupon.code,
                    'coupon_type': '1010',
                    'available_flg': str(coupon.available_flg),
                    'reason_cd': reason_cd
                }

            except NoResultFound:
                add_dict = {
                    'coupon_cd': req_coupon['coupon_cd'],
                    'coupon_type': '',
                    'available_flg': '0',
                    'reason_cd': '2010'
                }

            resp_data['coupons'].append(add_dict)

        return Response(
            content_type='application/json',
            charset='utf-8',
            text=json.dumps(resp_data, ensure_ascii=False)
        )

    @view_config(route_name='extauth_dummy.cancel_used_coupon')
    def eagles_cancel_used_coupon(self):
        # TODO fc_member_idのチェック。
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%s")
        client_name = self.request.POST['client_name']
        token = self.request.POST['token']
        used_coupons = json.loads(self.request.POST['used_coupons'])

        resp_data = {
            'status': 'OK',
            'timestamp': timestamp,
            'usage_type': '1010',
            'coupons': []
        }

        for req_coupon in used_coupons['coupons']:
            try:
                coupon = self.request.sa_session.query(EaglesCoupon).filter(
                    EaglesCoupon.code == req_coupon['coupon_cd']).one()

                if coupon.available_flg == 0:
                    coupon.available_flg = 1
                    self.request.sa_session.commit()
                    cancel_flg = '1'  # キャンセルに成功
                else:
                    cancel_flg = '0'  # キャンセルに失敗

                add_dict = {
                    'coupon_cd': coupon.code,
                    'coupon_type': '1010',
                    'cancel_flg': cancel_flg,
                    'reason_cd': '1010' if cancel_flg else '1020'
                }

            except NoResultFound:
                add_dict = {
                    'coupon_cd': req_coupon['coupon_cd'],
                    'coupon_type': '',
                    'available_flg': '0',
                    'reason_cd': '2010'
                }

            resp_data['coupons'].append(add_dict)

        return Response(
            content_type='application/json',
            charset='utf-8',
            text=json.dumps(resp_data, ensure_ascii=False)
        )
