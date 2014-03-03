# -*- coding:utf-8 -*-

""" TBA
"""

import logging
from datetime import datetime
from zope.interface import implementer
from . import models as m
from . import events
from .interfaces import (
    ICardBrandDetecter,
    IMulticheckoutSettingFactory,
    IMulticheckoutSettingListFactory,
    IMulticheckoutResponseFactory,
    IMulticheckoutImplFactory,
    IMulticheckout3DAPI,
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


def get_multicheckout_3d_api(request, override_name=None, now=None, default_item_cd=None, currency=None):
    impl = get_multicheckout_impl(request, override_name)
    return Multicheckout3DAPI(
        request=request,
        impl=impl,
        session=m._session, # XXX
        now=now,
        default_item_cd=default_item_cd,
        currency=currency
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

    def __init__(self, request, impl, session, now=None, default_item_cd=None, currency=None):
        if now is None:
            now = datetime.now()
        if default_item_cd is None:
            default_item_cd = self.DEFAULT_ITEM_CODE
        if currency is None:
            currency = self.CURRENCY
        self.request = request
        self.impl = impl
        self.session = session
        self.now = now
        self.default_item_cd = default_item_cd
        self.currency = currency

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

    def save_api_response(self, res):
        self.session.add(res)
        if hasattr(res, 'OrderNo') and hasattr(res, 'Storecd'):
            m.MultiCheckoutOrderStatus.set_status(res.OrderNo, res.Storecd, res.Status, u"call by %s" % self.request.url)
        self.session.commit()

    def secure3d_enrol(self, order_no, card_number, exp_year, exp_month, total_amount):
        """ セキュア3D認証要求 """

        order_no = maybe_unicode(order_no)
        enrol = m.Secure3DReqEnrolRequest(
            CardNumber=card_number,
            ExpYear=exp_year,
            ExpMonth=exp_month,
            TotalAmount=int(total_amount),
            Currency=self.currency,
        )
        self.session.add(enrol)
        self.session.commit()
        res = self.impl.secure3d_enrol(self, order_no, enrol)
        res.request = enrol
        events.Secure3DEnrolEvent.notify(self.request, order_no, res)
        self.save_api_response(res)
        return res


    def secure3d_auth(self, order_no, pares, md):
        """ セキュア3D認証結果取得"""

        order_no = maybe_unicode(order_no)
        auth = m.Secure3DAuthRequest(
            Md=md,
            PaRes=pares,
        )
        self.session.add(auth)
        self.session.commit()
        res = self.impl.secure3d_auth(self, order_no, auth)
        res.request = auth
        events.Secure3DAuthEvent.notify(self.request, order_no, res)
        self.save_api_response(res)
        return res


    def checkout_auth_secure3d(self, order_no, item_name, amount, tax, client_name, mail_address, card_no, card_limit, card_holder_name, mvn, xid, ts, eci, cavv, cavv_algorithm, free_data=None, item_cd=None):
        """ セキュア3D認証オーソリ """
        if item_cd is None:
            item_cd = self.default_item_cd
        order_no = maybe_unicode(order_no)
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
        )
        self.session.add(params)
        self.session.commit()
        res = self.impl.request_card_auth(self, order_no, params)
        res.request = params
        events.CheckoutAuthSecure3DEvent.notify(self.request, order_no, res)
        self.save_api_response(res)
        return res


    def checkout_sales(self, order_no):
        """ 売上確定 """

        order_no = maybe_unicode(order_no)
        res = self.impl.request_card_sales(self, order_no)
        events.CheckoutSalesSecure3DEvent.notify(self.request, order_no, res)
        self.save_api_response(res)
        return res


    def checkout_auth_cancel(self, order_no):
        """ オーソリキャンセル """

        order_no = maybe_unicode(order_no)
        res = self.impl.request_card_cancel_auth(self, order_no)
        events.CheckoutAuthCancelEvent.notify(self.request, order_no, res)
        self.save_api_response(res)
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
        params = m.MultiCheckoutRequestCardSalesPartCancel(
            SalesAmountCancellation=int(sales_amount_cancellation),
            TaxCarriageCancellation=int(tax_carriage_cancellation),
        )
        self.session.add(params)
        self.session.commit()
        res = self.impl.request_card_sales_part_cancel(self, order_no, params)
        events.CheckoutSalesPartCancelEvent.notify(self.request, order_no, res)
        self.save_api_response(res)
        return res


    def checkout_sales_cancel(self, order_no):
        """ 売上キャンセル"""

        order_no = maybe_unicode(order_no)
        res = self.impl.request_card_cancel_sales(self, order_no)
        events.CheckoutSalesCancelEvent.notify(self.request, order_no, res)
        self.save_api_response(res)
        return res


    def checkout_inquiry(self, order_no):
        """ 取引照会"""

        order_no = maybe_unicode(order_no)
        res = self.impl.request_card_inquiry(self, order_no)
        events.CheckoutInquiryEvent.notify(self.request, order_no, res)
        self.save_api_response(res)
        return res


    def checkout_auth_secure_code(self, order_no, item_name, amount, tax, client_name, mail_address, card_no, card_limit, card_holder_name, secure_code, free_data=None, item_cd=None):
        """ セキュアコードオーソリ """
        if item_cd is None:
            item_cd = self.default_item_cd
        order_no = maybe_unicode(order_no)
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
            )
        self.session.add(params)
        self.session.commit()
        res = self.impl.request_card_auth(self, order_no, params)
        res.request = params
        events.CheckoutAuthSecureCodeEvent.notify(self.request, order_no, res)
        self.save_api_response(res)
        return res

    def is_enable_secure3d(request, card_number):
        """ セキュア3D対応のカード会社か判定する """
        # とりあえず
        return len(card_number) == 16

    def get_order_status_by_order_no(self, order_no):
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



