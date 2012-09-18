# -*- coding:utf-8 -*-

""" TBA
"""

from pyramid.interfaces import IDict
from xml.etree import ElementTree as etree
import httplib
import urlparse
from . import models as m
from .interfaces import IMultiCheckout
from datetime import date
from . import logger
import ticketing.core.api as core_api

DEFAULT_ITEM_CODE = "120" # 通販

def get_multicheckout_setting(request, override_name):
    reg = request.registry
    if override_name:
        return m.MulticheckoutSetting.query.filter_by(shop_name=override_name).one()
    else:
        override_host = reg.settings.get('altair_checkout3d.override_host') or request.host
        organization = core_api.get_organization(request, override_host)
        return organization.multicheckout_settings[0]

def is_enable_secure3d(request, card_number):
    """ セキュア3D対応のカード会社か判定する """
    # とりあえず
    return len(card_number) == 16

def get_pares(request):
    """ get ``PARES`` value from request
    """
    return request.params['PaRes']

def get_md(request):
    """ get ``Md`` value from request
    """
    return request.params['MD']

def get_multicheckout_service(request):
    reg = request.registry
    # domain_candidates = reg.utilities.lookup([], IDict, 'altair.cart.domain.mapping')
    # host = reg.settings.get('altair_checkout3d.override_host') or request.host
    # shop_name = None
    # for k, v in domain_candidates.items():
    #     if host.startswith(k):
    #         shop_name = v
    # shop_name = reg.settings.get('altair_checkout3d.override_shop_name') or shop_name

    # if shop_name is None:
    #     logger.error('multicheckout setting for shop_name %s is not found' % host)

    # return reg.utilities.lookup([], IMultiCheckout, shop_name)

    orverride_name = reg.settings.get('altair_checkout3d.override_shop_name')
    setting = get_multicheckout_setting(request, override_name=orverride_name)
    if setting is None:
        raise Exception
    base_url = reg.settings['altair_checkout3d.base_url']
    checkout3d = Checkout3D(setting.auth_id, setting.auth_password, shop_code=setting.shop_id, api_base_url=base_url)
    return checkout3d

def secure3d_enrol(request, order_no, card_number, exp_year, exp_month, total_amount):
    service = get_multicheckout_service(request)
    enrol = m.Secure3DReqEnrolRequest(
        CardNumber=card_number,
        ExpYear=exp_year,
        ExpMonth=exp_month,
        TotalAmount=int(total_amount),
        Currency="392",
    )

    return service.secure3d_enrol(order_no, enrol)

def secure3d_auth(request, order_no, pares, md):
    auth = m.Secure3DAuthRequest(
        Md=md,
        PaRes=pares,
    )

    service = get_multicheckout_service(request)
    return service.secure3d_auth(order_no, auth)

def checkout_auth_secure3d(request,
                  order_no, item_name, amount, tax, client_name, mail_address,
                  card_no, card_limit, card_holder_name,
                  mvn, xid, ts, eci, cavv, cavv_algorithm,
                  free_data=None, item_cod=DEFAULT_ITEM_CODE, date=date):
    order_ymd = date.today().strftime('%Y%m%d')
    params = m.MultiCheckoutRequestCard(
        ItemCd=item_cod,
        ItemName=item_name,
        OrderYMD=order_ymd,
        SalesAmount=int(amount),
        TaxCarriage=tax,
        FreeData=free_data,
        ClientName=client_name,
        MailAddress=mail_address,
        MailSend='0',
        CardNo=card_no,
        CardLimit=card_limit,
        CardHolderName=card_holder_name,
        PayKindCd='10',
        PayCount=None,
        SecureKind='3',
        Mvn=mvn,
        Xid=xid,
        Ts=ts,
        ECI=eci,
        CAVV=cavv,
        CavvAlgorithm=cavv_algorithm,
    )
    service = get_multicheckout_service(request)
    return service.request_card_auth(order_no, params)

def checkout_sales_secure3d(request,
                  order_no, item_name, amount, tax, client_name, mail_address,
                  card_no, card_limit, card_holder_name,
                  mvn, xid, ts, eci, cavv, cavv_algorithm,
                  free_data=None, item_cod=DEFAULT_ITEM_CODE, date=date):
    order_ymd = date.today().strftime('%Y%m%d')
    params = m.MultiCheckoutRequestCard(
        ItemCd=item_cod,
        ItemName=item_name,
        OrderYMD=order_ymd,
        SalesAmount=int(amount),
        TaxCarriage=tax,
        FreeData=free_data,
        ClientName=client_name,
        MailAddress=mail_address,
        MailSend='0',
        CardNo=card_no,
        CardLimit=card_limit,
        CardHolderName=card_holder_name,
        PayKindCd='10',
        PayCount=None,
        SecureKind='3',
        Mvn=mvn,
        Xid=xid,
        Ts=ts,
        ECI=eci,
        CAVV=cavv,
        CavvAlgorithm=cavv_algorithm,
    )
    service = get_multicheckout_service(request)
    return service.request_card_sales(order_no, params)

def checkout_auth_cancel(request, order_no):
    service = get_multicheckout_service(request)
    return service.request_card_cancel_auth(order_no)

def checkout_sales_cancel(request, order_no):
    service = get_multicheckout_service(request)
    return service.request_card_cancel_sales(order_no)

def checkout_inquiry(request, order_no):
    service = get_multicheckout_service(request)
    return service.request_card_inquiry(order_no)

def checkout_auth_secure_code(request, order_no, item_name, amount, tax, client_name, mail_address,
                     card_no, card_limit, card_holder_name,
                     secure_code,
                     free_data=None, item_cd=DEFAULT_ITEM_CODE, date=date):

    order_ymd = date.today().strftime('%Y%m%d')
    params = m.MultiCheckoutRequestCard(
        ItemCd=item_cd,
        ItemName=item_name,
        OrderYMD=order_ymd,
        SalesAmount=int(amount),
        TaxCarriage=tax,
        FreeData=free_data,
        ClientName=client_name,
        MailAddress=mail_address,
        MailSend='0',

        CardNo=card_no,
        CardLimit=card_limit,
        CardHolderName=card_holder_name,

        PayKindCd='10',
        PayCount=None,
        SecureKind='2',
        SecureCode=secure_code,
    )
    service = get_multicheckout_service(request)
    return service.request_card_auth(order_no, params)


def checkout_sales_secure_code(request, order_no, item_name, amount, tax, client_name, mail_address,
                     card_no, card_limit, card_holder_name,
                     secure_code,
                     free_data=None, item_cd=DEFAULT_ITEM_CODE, date=date):

    order_ymd = date.today().strftime('%Y%m%d')
    params = m.MultiCheckoutRequestCard(
        ItemCd=item_cd,
        ItemName=item_name,
        OrderYMD=order_ymd,
        SalesAmount=int(amount),
        TaxCarriage=tax,
        FreeData=free_data,
        ClientName=client_name,
        MailAddress=mail_address,
        MailSend='0',

        CardNo=card_no,
        CardLimit=card_limit,
        CardHolderName=card_holder_name,

        PayKindCd='10',
        PayCount=None,
        SecureKind='2',
        SecureCode=secure_code,
    )
    service = get_multicheckout_service(request)
    return service.request_card_sales(order_no, params)

class MultiCheckoutAPIError(Exception):
    pass

class Checkout3D(object):
    _httplib = httplib

    def __init__(self, auth_id, auth_password, shop_code, api_base_url):
        self.auth_id = auth_id
        self.auth_password = auth_password
        self.shop_code = shop_code
        self.api_base_url = api_base_url

    @property
    def auth_header(self):
        return {"Authorization": "Basic " + (self.auth_id + ":" + self.auth_password).encode('base64').strip()}

    def secure3d_enrol_url(self, order_no):
        return self.api_url + "/3D-Secure/OrderNo/%(order_no)s/Enrol" % dict(order_no=order_no)

    def secure3d_auth_url(self, order_no):
        return self.api_url + "/3D-Secure/OrderNo/%(order_no)s/Auth" % dict(order_no=order_no)

    def card_check_url(self, order_no):
        return self.api_url + "/card/OrderNo/%(order_no)s/Check" % dict(order_no=order_no)

    def card_auth_url(self, order_no):
        return self.api_url + "/card/OrderNo/%(order_no)s/Auth" % dict(order_no=order_no)

    def card_auth_cancel_url(self, order_no):
        return self.api_url + "/card/OrderNo/%(order_no)s/AuthCan" % dict(order_no=order_no)

    def card_sales_url(self, order_no):
        return self.api_url + "/card/OrderNo/%(order_no)s/Sales" % dict(order_no=order_no)

    def card_cancel_sales_url(self, order_no):
        return self.api_url + "/card/OrderNo/%(order_no)s/SalesCan" % dict(order_no=order_no)

    def card_inquiry_url(self, order_no):
        return self.api_url + "/card/OrderNo/%(order_no)s" % dict(order_no=order_no)

    def secure3d_enrol(self, order_no, enrol):
        message = self._create_secure3d_enrol_xml(enrol)
        url = self.secure3d_enrol_url(order_no)
        res = self._request(url, message)
        logger.debug("got response %s" % etree.tostring(res))
        return self._parse_secure3d_enrol_response(res)

    def secure3d_auth(self, order_no, auth):
        message = self._create_secure3d_auth_xml(auth)
        url = self.secure3d_auth_url(order_no)
        res = self._request(url, message)
        logger.debug("got response %s" % etree.tostring(res))
        return self._parse_secure3d_auth_response(res)

    def request_card_check(self, order_no, card_auth):
        message = self._create_request_card_xml(card_auth, check=True)
        url = self.card_check_url(order_no)
        res = self._request(url, message)
        logger.debug("got response %s" % etree.tostring(res))
        return self._parse_response_card_xml(res)

    def request_card_auth(self, order_no, card_auth):
        message = self._create_request_card_xml(card_auth, check=True)
        url = self.card_auth_url(order_no)
        res = self._request(url, message)
        logger.debug("got response %s" % etree.tostring(res))
        return self._parse_response_card_xml(res)

    def request_card_cancel_auth(self, order_no):
        url = self.card_auth_cancel_url(order_no)
        res = self._request(url)
        logger.debug("got response %s" % etree.tostring(res))
        return self._parse_response_card_xml(res)

    def request_card_sales(self, order_no, card_auth):
        message = self._create_request_card_xml(card_auth, check=True)
        url = self.card_sales_url(order_no)
        res = self._request(url, message)
        logger.debug("got response %s" % etree.tostring(res))
        return self._parse_response_card_xml(res)

    def request_card_cancel_sales(self, order_no):
        url = self.card_cancel_sales_url(order_no)
        res = self._request(url)
        logger.debug("got response %s" % etree.tostring(res))
        return self._parse_response_card_xml(res)

    def request_card_inquiry(self, order_no):
        url = self.card_inquiry_url(order_no)
        res = self._request(url)
        logger.debug("got response %s" % etree.tostring(res))
        return self._parse_inquiry_response_card_xml(res)


    def _request(self, url, message=None):
        content_type = "application/xhtml+xml;charset=UTF-8"
        #body = etree.tostring(message, encoding='utf-8') if message else ''
        body = etree.tostring(message) if message else ''
        url_parts = urlparse.urlparse(url)

        if url_parts.scheme == "http":
            http = self._httplib.HTTPConnection(host=url_parts.hostname, port=url_parts.port)
        elif url_parts.scheme == "https":
            http = self._httplib.HTTPSConnection(host=url_parts.hostname, port=url_parts.port)
        else:
            raise ValueError, "unknown scheme %s" % (url_parts.scheme)

        headers = {
            "Content-Type": content_type,
        }

        headers.update(self.auth_header)

        logger.debug("request %s body = %s" % (url, body))
        http.request(
            "POST", url_parts.path, body=body,
            headers=headers)
        res = http.getresponse()
        try:
            logger.debug('%(url)s %(status)s %(reason)s' % dict(
                url=url,
                status=res.status,
                reason=res.reason,
            ))
            if res.status != 200:
                raise MultiCheckoutAPIError, res.reason

            return etree.parse(res).getroot()
        finally:
            res.close()

    @property
    def api_url(self):
        return self.api_base_url.rstrip('/') + '/'  + self.shop_code.lstrip('/')

    def _add_param(self, parent, name, value, optional=False):

        if value is None:
            if optional:
                return None
            else:
                raise ValueError, name
        e = etree.SubElement(parent, name)
        e.text = value
        return e

    def _create_secure3d_enrol_xml(self, secure3d_enrol):
        message = etree.Element("Message")
        self._add_param(message, 'CardNumber', secure3d_enrol.CardNumber)
        self._add_param(message, 'ExpYear', secure3d_enrol.ExpYear)
        self._add_param(message, 'ExpMonth', secure3d_enrol.ExpMonth)
        self._add_param(message, 'TotalAmount', str(secure3d_enrol.TotalAmount))
        self._add_param(message, 'Currency', secure3d_enrol.Currency)

        return message


    def _create_secure3d_auth_xml(self, secure3d_auth):
        message = etree.Element("Message")
        self._add_param(message, 'Md', secure3d_auth.Md)
        self._add_param(message, 'PaRes', secure3d_auth.PaRes)

        return message

    def _create_request_card_xml(self, card_auth, check=False):
        """
        :param card_auth: :class:`.models.MultiCheckoutRequestCard`

        """

        # メッセージタグ <Message>
        message = etree.Element('Message')

        # オーソリ情報 <Message><Auth>
        auth = etree.SubElement(message, 'Auth')

        # 注文情報 <Message><Auth><Order>
        order = etree.SubElement(auth, 'Order')
        # 商品コード
        self._add_param(order, 'ItemCd', card_auth.ItemCd, optional=True)
        self._add_param(order, 'ItemName', card_auth.ItemName, optional=True)
        self._add_param(order, 'OrderYMD', card_auth.OrderYMD, optional=check)
        self._add_param(order, 'SalesAmount', str(card_auth.SalesAmount), optional=check)
        self._add_param(order, 'TaxCarriage', str(card_auth.TaxCarriage), optional=True)
        self._add_param(order, 'FreeData', card_auth.FreeData, optional=True)
        self._add_param(order, 'ClientName', card_auth.ClientName, optional=check)
        self._add_param(order, 'MailAddress', card_auth.MailAddress, optional=card_auth.MailSend=='1')
        self._add_param(order, 'MailSend', card_auth.MailSend)


        # カード情報 <Message><Auth><Card>
        card = etree.SubElement(auth, 'Card')
        self._add_param(card, 'CardNo', card_auth.CardNo)
        self._add_param(card, 'CardLimit', card_auth.CardLimit)
        self._add_param(card, 'CardHolderName', card_auth.CardHolderName, optional=check)
        self._add_param(card, 'PayKindCd', card_auth.PayKindCd, optional=check)
        self._add_param(card, 'PayCount', card_auth.PayCount, optional=card_auth.PayKindCd=='10')
        self._add_param(card, 'SecureKind', card_auth.SecureKind)

        # CVVチェック
        if card_auth.SecureKind == '2':
            secure_code = etree.SubElement(auth, 'SecureCd')
            self._add_param(secure_code, 'Code', card_auth.SecureCode, optional=card_auth.SecureKind != '2')

        # セキュア3D
        if card_auth.SecureKind == '3':
            secure_3d = etree.SubElement(auth, 'Secure3D')
            self._add_param(secure_3d, 'Mvn', card_auth.Mvn, optional=card_auth.SecureKind != '3')
            self._add_param(secure_3d, 'Xid', card_auth.Xid, optional=card_auth.SecureKind != '3')
            self._add_param(secure_3d, 'Ts', card_auth.Ts, optional=card_auth.SecureKind != '3')
            self._add_param(secure_3d, 'ECI', card_auth.ECI, optional=card_auth.SecureKind != '3')
            self._add_param(secure_3d, 'CAVV', card_auth.CAVV, optional=card_auth.SecureKind != '3')
            self._add_param(secure_3d, 'CavvAlgorithm', card_auth.CavvAlgorithm, optional=card_auth.SecureKind != '3')
            self._add_param(secure_3d, 'CardNo', card_auth.CardNo, optional=card_auth.SecureKind != '3')

        return message

    def _parse_response_card_xml(self, element):
        card_response = m.MultiCheckoutResponseCard()
        assert element.tag == "Message"
        for e in element:
            if e.tag == "Request":
                for sube in e:
                    if sube.tag == "BizClassCd":
                        card_response.BizClassCd = sube.text
                    elif sube.tag == "Storecd":
                        card_response.Storecd = sube.text
            if e.tag == "Result":
                for sube in e:
                    if sube.tag == "SettlementInfo":
                        for ssube in sube:
                            if ssube.tag == "OrderNo":
                                card_response.OrderNo = ssube.text
                            elif ssube.tag == "Status":
                                card_response.Status = ssube.text
                            elif ssube.tag == "PublicTranId":
                                card_response.PublicTranId = ssube.text
                            elif ssube.tag == "AheadComCd":
                                card_response.AheadComCd = ssube.text
                            elif ssube.tag == "ApprovalNo":
                                card_response.ApprovalNo = ssube.text
                            elif ssube.tag == "CardErrorCd":
                                card_response.CardErrorCd = ssube.text
                            elif ssube.tag == "ReqYmd":
                                card_response.ReqYmd = ssube.text
                            elif ssube.tag == "CmnErrorCd":
                                card_response.CmnErrorCd = ssube.text
        return card_response

    def _parse_inquiry_response_card_xml(self, element):
        inquiry_card_response = m.MultiCheckoutInquiryResponseCard()
        assert element.tag == "Message"
        for e in element:
            if e.tag == "Request":
                for sube in e:
                    if sube.tag == "Storecd":
                        inquiry_card_response.Storecd = sube.text
            if e.tag == "Result":
                for sube in e:
                    if sube.tag == "Info":
                        for ssube in sube:
                            if ssube.tag == "EventDate":
                                inquiry_card_response.EventDate = ssube.text
                            elif ssube.tag == "Status":
                                inquiry_card_response.Status = ssube.text
                            elif ssube.tag == "CardErrorCd":
                                inquiry_card_response.CardErrorCd = ssube.text
                            elif ssube.tag == "ApprovalNo":
                                inquiry_card_response.ApprovalNo = ssube.text
                            elif ssube.tag == "CmnErrorCd":
                                inquiry_card_response.CmnErrorCd = ssube.text
                    elif sube.tag == "Order":
                        for ssube in sube:
                            if ssube.tag == "OrderNo":
                                inquiry_card_response.OrderNo = ssube.text
                            elif ssube.tag == "ItemName":
                                inquiry_card_response.ItemName = ssube.text
                            elif ssube.tag == "OrderYMD":
                                inquiry_card_response.OrderYMD = ssube.text
                            elif ssube.tag == "SalesAmount":
                                inquiry_card_response.SalesAmount = ssube.text
                            elif ssube.tag == "FreeData":
                                inquiry_card_response.FreeData = ssube.text
                    elif sube.tag == "ClientInfo":
                        for ssube in sube:
                            if ssube.tag == "ClientName":
                                inquiry_card_response.ClientName = ssube.text
                            elif ssube.tag == "MailAddress":
                                inquiry_card_response.MailAddress = ssube.text
                            elif ssube.tag == "MailSend":
                                inquiry_card_response.MailSend = ssube.text
                    elif sube.tag == "CardInfo":
                        for ssube in sube:
                            if ssube.tag == "CardNo":
                                inquiry_card_response.CardNo = ssube.text
                            elif ssube.tag == "CardLimit":
                                inquiry_card_response.CardLimit = ssube.text
                            elif ssube.tag == "CardHolderName":
                                inquiry_card_response.CardHolderName = ssube.text
                            elif ssube.tag == "PayKindCd":
                                inquiry_card_response.PayKindCd = ssube.text
                            elif ssube.tag == "PayCount":
                                inquiry_card_response.PayCount = ssube.text
                            elif ssube.tag == "SecureKind":
                                inquiry_card_response.SecureKind = ssube.text
                    elif sube.tag == "History":
                        history = m.MultiCheckoutInquiryResponseCardHistory(inquiry=inquiry_card_response)
                        for ssube in sube:
                            if ssube.tag == "BizClassCd":
                                history.BizClassCd = ssube.text
                            elif ssube.tag == "EventDate":
                                history.EventDate = ssube.text
                            elif ssube.tag == "SalesAmount":
                                history.SalesAmount = int(ssube.text)

        return inquiry_card_response

    def _parse_secure3d_enrol_response(self, element):
        enrol_response = m.Secure3DReqEnrolResponse()
        assert element.tag == "Message"
        for e in element:
            if e.tag == 'Md':
                enrol_response.Md = e.text
            elif e.tag == 'ErrorCd':
                enrol_response.ErrorCd = e.text
            elif e.tag == 'RetCd':
                enrol_response.RetCd = e.text
            elif e.tag == 'AcsUrl':
                enrol_response.AcsUrl = e.text
            elif e.tag == 'PaReq':
                enrol_response.PaReq = e.text
        return enrol_response

    def _parse_secure3d_auth_response(self, element):
        auth_response = m.Secure3DAuthResponse()
        assert element.tag == "Message"
        for e in element:
            if e.tag == 'ErrorCd':
                auth_response.ErrorCd = e.text
            elif e.tag == 'RetCd':
                auth_response.RetCd = e.text
            elif e.tag == 'Xid':
                auth_response.Xid = e.text
            elif e.tag == 'Ts':
                auth_response.Ts = e.text
            elif e.tag == 'Cavva':
                auth_response.Cavva = e.text
            elif e.tag == 'Cavv':
                auth_response.Cavv = e.text
            elif e.tag == 'Eci':
                auth_response.Eci = e.text
            elif e.tag == 'Mvn':
                auth_response.Mvn = e.text
        return auth_response
