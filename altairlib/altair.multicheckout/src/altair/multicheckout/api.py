# -*- coding:utf-8 -*-

""" TBA
"""

import logging
from datetime import datetime, timedelta
from zope.interface import implementer
from sqlalchemy.orm import contains_eager
from . import models as m
from . import events
from .interfaces import (
    ICardBrandDetecter,
    IMulticheckoutSettingFactory,
    IMulticheckoutSettingListFactory,
    IMulticheckoutResponseFactory,
    IMulticheckoutImplFactory,
    IMulticheckout3DAPI,
    IMulticheckoutOrderNoDecorator,
)
from .util import ahead_coms, maybe_unicode

logger = logging.getLogger(__name__)

def get_multicheckout_setting(request, override_name):
    reg = request.registry
    return reg.getUtility(IMulticheckoutSettingFactory)(request, override_name)

def get_all_multicheckout_settings(request):
    reg = request.registry
    return reg.getUtility(IMulticheckoutSettingListFactory)(request)


def get_multicheckout_impl(request, override_name=None):
    return request.registry.getUtility(IMulticheckoutImplFactory)(request, override_name)


def get_order_no_decorator(request):
    reg = request.registry
    retval = reg.queryUtility(IMulticheckoutOrderNoDecorator)
    if retval is None:
        from . import IdentityDecorator
        retval = IdentityDecorator()
    return retval


def get_multicheckout_3d_api(request, override_name=None, now=None, default_item_cd=None, currency=None):
    impl = get_multicheckout_impl(request, override_name)
    return Multicheckout3DAPI(
        request=request,
        impl=impl,
        session=m._session, # XXX
        now=now,
        default_item_cd=default_item_cd,
        currency=currency,
        order_no_decorator=get_order_no_decorator(request)
        )


def detect_card_brand(request, card_number):
    detecter = request.registry.getUtility(ICardBrandDetecter)
    return detecter(card_number)

def get_card_ahead_com_name(request, code):
    if code in ahead_coms:
        return ahead_coms[code]
    return u"その他"


@implementer(IMulticheckoutResponseFactory, IMulticheckout3DAPI)
class Multicheckout3DAPI(object):
    DEFAULT_ITEM_CODE = u"120"  # 通販
    CURRENCY = u"392" # 日本円

    def __init__(self, request, impl, session, order_no_decorator, now=None, default_item_cd=None, currency=None):
        if now is None:
            now = datetime.now()
        if default_item_cd is None:
            default_item_cd = self.DEFAULT_ITEM_CODE
        if currency is None:
            currency = self.CURRENCY
        self.request = request
        self.impl = impl
        self.session = session
        self.order_no_decorator = order_no_decorator.decorate
        self.now = now
        self.default_item_cd = default_item_cd
        self.currency = currency

    def _decorate_order_no(self, order_no):
        return self.order_no_decorator(order_no)

    def create_multicheckout_response_card(self):
        return m.MultiCheckoutResponseCard()

    def create_multicheckout_inquiry_response_card(self):
        return m.MultiCheckoutInquiryResponseCard()

    def create_multicheckout_inquiry_response_card_history(self):
        return m.MultiCheckoutInquiryResponseCardHistory()

    def create_secure3d_req_enrol_response(self):
        return m.Secure3DReqEnrolResponse()

    def create_secure3d_auth_response(self):
        return m.Secure3DAuthResponse()

    def save_api_response(self, res, req, invoker=None):
        self.session.add(res)
        try:
            if hasattr(res, 'OrderNo') and hasattr(res, 'Storecd'):
                status = res.Status
                if res.CmnErrorCd == '001407':  # 取引詳細操作不可
                    status = u"-10"
                if invoker is None:
                    invoker = u"call by %s" % self.request.url
                amount = None
                if hasattr(res, 'SalesAmount'):
                    amount = res.SalesAmount
                else:
                    if hasattr(req, 'SalesAmount'):
                        amount = req.SalesAmount
                    elif hasattr(req, 'SalesAmountCancellation'):
                        prev_status = m.MultiCheckoutOrderStatus.get_or_create(res.OrderNo, res.Storecd, session=self.session)
                        if prev_status.SalesAmount is not None:
                            amount = prev_status.SalesAmount - req.SalesAmountCancellation
                m.MultiCheckoutOrderStatus.set_status(res.OrderNo, res.Storecd, status, amount, invoker, session=self.session)
        finally:
            self.session.commit()

    def _get_order_status(self, order_no):
        return self.session.query(m.MultiCheckoutOrderStatus) \
            .filter(m.MultiCheckoutOrderStatus.OrderNo == order_no) \
            .filter(m.MultiCheckoutOrderStatus.Storecd == self.impl.shop_code) \
            .first()

    def secure3d_enrol(self, order_no, card_number, exp_year, exp_month, total_amount):
        """ セキュア3D認証要求 """
        order_no = maybe_unicode(order_no)
        order_no = self._decorate_order_no(order_no)
        enrol = m.Secure3DReqEnrolRequest(
            CardNumber=card_number,
            ExpYear=exp_year,
            ExpMonth=exp_month,
            TotalAmount=int(total_amount),
            Currency=self.currency,
        )
        self.session.add(enrol)
        try:
            res = self.impl.secure3d_enrol(self, order_no, enrol)
        finally:
            self.session.commit()
        res.request = enrol
        events.Secure3DEnrolEvent.notify(self.request, order_no, res)
        self.save_api_response(res, enrol)
        return res


    def secure3d_auth(self, order_no, pares, md):
        """ セキュア3D認証結果取得"""
        order_no = maybe_unicode(order_no)
        order_no = self._decorate_order_no(order_no)
        auth = m.Secure3DAuthRequest(
            Md=md,
            PaRes=pares,
        )
        self.session.add(auth)
        try:
            res = self.impl.secure3d_auth(self, order_no, auth)
        finally:
            self.session.commit()
        res.request = auth
        events.Secure3DAuthEvent.notify(self.request, order_no, res)
        self.save_api_response(res, auth)
        return res


    def checkout_auth_secure3d(self, order_no, item_name, amount, tax, client_name, mail_address, card_no, card_limit, card_holder_name, mvn, xid, ts, eci, cavv, cavv_algorithm, free_data=None, item_cd=None):
        """ セキュア3D認証オーソリ """
        if item_cd is None:
            item_cd = self.default_item_cd
        order_no = maybe_unicode(order_no)
        order_no = self._decorate_order_no(order_no)
        order_ymd = self.now.strftime('%Y%m%d').decode('ascii')
        params = m.MultiCheckoutRequestCard(
            ItemCd=item_cd,
            ItemName=item_name,
            OrderYMD=order_ymd,
            SalesAmount=int(amount),
            TaxCarriage=tax,
            FreeData=free_data,
            ClientName=client_name,
            MailAddress=mail_address,
            MailSend=u'0',
            CardNo=card_no,
            CardLimit=card_limit,
            CardHolderName=card_holder_name,
            PayKindCd=u'10',
            PayCount=None,
            SecureKind=u'3',
            Mvn=mvn,
            Xid=xid,
            Ts=ts,
            ECI=eci,
            CAVV=cavv,
            CavvAlgorithm=cavv_algorithm,
            card_brand=detect_card_brand(self.request, card_no)
            )
        self.session.add(params)
        try:
            res = self.impl.request_card_auth(self, order_no, params)
        finally:
            self.session.commit()
        res.request = params
        events.CheckoutAuthSecure3DEvent.notify(self.request, order_no, res)
        self.save_api_response(res, params)
        return res


    def checkout_sales(self, order_no):
        """ 売上確定 """
        order_no = maybe_unicode(order_no)
        order_no = self._decorate_order_no(order_no)
        res = self.impl.request_card_sales(self, order_no)
        events.CheckoutSalesSecure3DEvent.notify(self.request, order_no, res)
        self.save_api_response(res, None)
        return res


    def checkout_auth_cancel(self, order_no):
        """ オーソリキャンセル """
        order_no = maybe_unicode(order_no)
        order_no = self._decorate_order_no(order_no)
        status = self._get_order_status(order_no)
        if status is not None and status.KeepAuthFor:
            return None
        res = self.impl.request_card_cancel_auth(self, order_no)
        events.CheckoutAuthCancelEvent.notify(self.request, order_no, res)
        self.save_api_response(res, None)
        return res


    def checkout_sales_different_amount(self, order_no, different_amount):
        """ オーソリ差額売上確定
        オーソリ時金額で確定後に差額を一部キャンセルする
        """
        res = self.checkout_sales(order_no)
        if res.CmnErrorCd != '000000':
            logger.error(u"差額売上確定中に売上確定でエラーが発生しました")
            return res
        logger.info("call sales_part_cancel for %d" % different_amount)
        if different_amount > 0:
            res = self.checkout_sales_part_cancel(order_no, different_amount, 0)
            if res.CmnErrorCd != '000000':
                logger.error(u"差額売上確定中に一部払い戻しでエラーが発生しました")
                return res
        return res

    def checkout_sales_part_cancel(self, order_no, sales_amount_cancellation, tax_carriage_cancellation):
        """ 一部払い戻し """
        order_no = maybe_unicode(order_no)
        order_no = self._decorate_order_no(order_no)
        params = m.MultiCheckoutRequestCardSalesPartCancel(
            SalesAmountCancellation=int(sales_amount_cancellation),
            TaxCarriageCancellation=int(tax_carriage_cancellation),
        )
        self.session.add(params)
        try:
            res = self.impl.request_card_sales_part_cancel(self, order_no, params)
        finally:
            self.session.commit()
        events.CheckoutSalesPartCancelEvent.notify(self.request, order_no, res)
        self.save_api_response(res, params)
        return res


    def checkout_sales_cancel(self, order_no):
        """ 売上キャンセル"""
        order_no = maybe_unicode(order_no)
        order_no = self._decorate_order_no(order_no)
        res = self.impl.request_card_cancel_sales(self, order_no)
        events.CheckoutSalesCancelEvent.notify(self.request, order_no, res)
        self.save_api_response(res, None)
        return res

    def get_authorized_amount(self, order_no):
        order_no = maybe_unicode(order_no)
        order_no = self._decorate_order_no(order_no)
        status = self._get_order_status(order_no)
        if status is not None:
            return status.SalesAmount
        else:
            return None

    def keep_authorization(self, order_no, for_what):
        order_no = maybe_unicode(order_no)
        order_no = self._decorate_order_no(order_no)
        status = self._get_order_status(order_no)
        if status is None:
            return
        status.KeepAuthFor = for_what
        self.session.add(status)
        self.session.commit()

    def authorization_kept_for(self, order_no):
        order_no = maybe_unicode(order_no)
        order_no = self._decorate_order_no(order_no)
        status = self._get_order_status(order_no)
        if status is not None:
            # 空文字列が入っていたとしても None を返したい
            return status.KeepAuthFor if status.KeepAuthFor else None
        else:
            return None

    def schedule_cancellation(self, order_no, scheduled_at, eventual_sales_amount=None, tax_carriage_amount_to_cancel=None):
        order_no = maybe_unicode(order_no)
        order_no = self._decorate_order_no(order_no)
        status = self._get_order_status(order_no)
        if status is None:
            return
        assert status.is_settled
        status.CancellationScheduledAt = scheduled_at
        if eventual_sales_amount is None:
            eventual_sales_amount = 0
        if tax_carriage_amount_to_cancel is None:
            tax_carriage_amount_to_cancel = 0
        status.EventualSalesAmount = eventual_sales_amount 
        status.TaxCarriageAmountToCancel = tax_carriage_amount_to_cancel
        self.session.add(status)
        self.session.commit()

    def unschedule_cancellation(self, order_no):
        order_no = maybe_unicode(order_no)
        order_no = self._decorate_order_no(order_no)
        status = self._get_order_status(order_no)
        if status is None:
            return
        status.CancellationScheduledAt = None
        status.EventualSalesAmount = None
        status.TaxCarriageAmountToCancel = None
        self.session.add(status)
        self.session.commit()

    def checkout_inquiry(self, order_no, invoker=None):
        """ 取引照会"""
        order_no = maybe_unicode(order_no)
        order_no = self._decorate_order_no(order_no)
        res = self.impl.request_card_inquiry(self, order_no)
        events.CheckoutInquiryEvent.notify(self.request, order_no, res)
        self.save_api_response(res, None, invoker=invoker)
        return res


    def checkout_auth_secure_code(self, order_no, item_name, amount, tax, client_name, mail_address, card_no, card_limit, card_holder_name, secure_code, free_data=None, item_cd=None):
        """ セキュアコードオーソリ """
        if item_cd is None:
            item_cd = self.default_item_cd
        order_no = maybe_unicode(order_no)
        order_no = self._decorate_order_no(order_no)
        order_ymd = self.now.strftime('%Y%m%d').decode('ascii')
        params = m.MultiCheckoutRequestCard(
            ItemCd=item_cd,
            ItemName=item_name,
            OrderYMD=order_ymd,
            SalesAmount=int(amount),
            TaxCarriage=tax,
            FreeData=free_data,
            ClientName=client_name,
            MailAddress=mail_address,
            MailSend=u'0',

            CardNo=card_no,
            CardLimit=card_limit,
            CardHolderName=card_holder_name,

            PayKindCd=u'10',
            PayCount=None,
            SecureKind=u'2',
            SecureCode=secure_code,
            card_brand=detect_card_brand(self.request, card_no)
            )
        self.session.add(params)
        try:
            res = self.impl.request_card_auth(self, order_no, params)
        finally:
            self.session.commit()
        res.request = params
        events.CheckoutAuthSecureCodeEvent.notify(self.request, order_no, res)
        self.save_api_response(res, params)
        return res

    def is_enable_secure3d(request, card_number):
        """ セキュア3D対応のカード会社か判定する """
        # とりあえず
        return len(card_number) == 16

    def get_order_status_by_order_no(self, order_no):
        order_no = maybe_unicode(order_no)
        order_no = self._decorate_order_no(order_no)
        return self.session.query(m.MultiCheckoutOrderStatus) \
            .filter(m.MultiCheckoutOrderStatus.OrderNo == order_no) \
            .first()

    def get_pares(self):
        """ get ``PARES`` value from request
        """
        return self.request.params['PaRes']


    def get_md(self):
        """ get ``Md`` value from request
        """
        return self.request.params['MD']

    def get_transaction_info(self, order_no):
        order_no = maybe_unicode(order_no)
        order_no = self._decorate_order_no(order_no)
        q = self.session.query(m.MultiCheckoutResponseCard) \
            .outerjoin(m.MultiCheckoutResponseCard.request) \
            .options(contains_eager(m.MultiCheckoutResponseCard.request)) \
            .filter(m.MultiCheckoutResponseCard.OrderNo == order_no)
        standard_info = [
            {
                'status': resp.Status,
                'approval_no': resp.ApprovalNo,
                'ahead_com_cd': resp.AheadComCd,
                'error_cd': resp.CmnErrorCd,
                'card_error_cd': resp.CardErrorCd,
                'card_no': resp.request and resp.request.CardNo,
                'card_limit': resp.request and resp.request.CardLimit,
                'card_limit': resp.request and resp.request.CardLimit,
                'secure_kind': resp.request and resp.request.SecureKind,
                'card_brand': resp.request and resp.request.card_brand,
                }
            for resp in q
            ]

        q = self.session.query(m.Secure3DAuthResponse) \
            .outerjoin(m.Secure3DAuthResponse.request) \
            .options(contains_eager(m.Secure3DAuthResponse.request)) \
            .filter(m.Secure3DAuthResponse.OrderNo == order_no)
        secure3d_info = [
            {
                'error_cd': resp.ErrorCd,
                'secure3d_ret_cd': resp.RetCd,
                }
            for resp in q
            ]
        return standard_info, secure3d_info


def remove_default_session():
    m._session.remove()
