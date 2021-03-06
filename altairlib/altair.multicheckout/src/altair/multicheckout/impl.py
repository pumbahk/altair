# encoding: utf-8

import logging
import httplib
import urlparse
import ssl
import socket
from xml.etree import ElementTree as etree
from .util import maybe_unicode, sanitize_card_number
from .exceptions import MultiCheckoutAPIError, MultiCheckoutAPITimeoutError

logger = logging.getLogger(__name__)

class Checkout3D(object):
    _httplib = httplib

    def __init__(self, auth_id, auth_password, shop_code, api_base_url, api_timeout):
        if auth_id is None:
            raise TypeError('auth_id may not be None')
        if auth_password is None:
            raise TypeError('auth_password may not be None')
        if shop_code is None:
            raise TypeError('shop_code may not be None')
        if api_base_url is None:
            raise TypeError('api_base_url may not be None')
        self.auth_id = auth_id
        self.auth_password = auth_password
        self.shop_code = shop_code
        self.api_base_url = api_base_url
        self.api_timeout = float(api_timeout)

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

    def card_sales_part_cancel_url(self, order_no):
        return self.api_url + "/card/OrderNo/%(order_no)s/SalesPartCan" % dict(order_no=order_no)

    def card_cancel_sales_url(self, order_no):
        return self.api_url + "/card/OrderNo/%(order_no)s/SalesCan" % dict(order_no=order_no)

    def card_inquiry_url(self, order_no):
        return self.api_url + "/card/OrderNo/%(order_no)s" % dict(order_no=order_no)

    def secure3d_enrol(self, response_factory, order_no, enrol):
        message = self._create_secure3d_enrol_xml(enrol)
        url = self.secure3d_enrol_url(order_no)
        res = self._request(url, message)
        logger.debug("got response %s" % etree.tostring(res))
        res_obj = self._parse_secure3d_enrol_response(response_factory, res)
        res_obj.OrderNo = order_no
        return res_obj

    def secure3d_auth(self, response_factory, order_no, auth):
        message = self._create_secure3d_auth_xml(auth)
        url = self.secure3d_auth_url(order_no)
        res = self._request(url, message)
        logger.debug("got response %s" % etree.tostring(res))
        res_obj = self._parse_secure3d_auth_response(response_factory, res)
        res_obj.OrderNo = order_no
        return res_obj

    def request_card_check(self, response_factory, order_no, card_auth):
        message = self._create_request_card_xml(card_auth, check=True)
        url = self.card_check_url(order_no)
        res = self._request(url, message)
        logger.debug("got response %s" % etree.tostring(res))
        return self._parse_response_card_xml(response_factory, res)

    def request_card_auth(self, response_factory, order_no, card_auth, forced_3d_auth=False):
        message = self._create_request_card_xml(card_auth, check=True, forced_3d_auth=forced_3d_auth)
        url = self.card_auth_url(order_no)
        res = self._request(url, message)
        logger.debug("got response %s" % etree.tostring(res))
        return self._parse_response_card_xml(response_factory, res)

    def request_card_cancel_auth(self, response_factory, order_no):
        url = self.card_auth_cancel_url(order_no)
        res = self._request(url)
        logger.debug("got response %s" % etree.tostring(res))
        return self._parse_response_card_xml(response_factory, res)

    def request_card_sales(self, response_factory, order_no):
        url = self.card_sales_url(order_no)
        res = self._request(url)
        logger.debug("got response %s" % etree.tostring(res))
        return self._parse_response_card_xml(response_factory, res)

    def request_card_sales_part_cancel(self, response_factory, order_no, params):
        message = self._create_request_card_sales_part_cancel_xml(params)
        url = self.card_sales_part_cancel_url(order_no)
        res = self._request(url, message)
        logger.debug("got response %s" % etree.tostring(res))
        return self._parse_response_card_xml(response_factory, res)

    def request_card_cancel_sales(self, response_factory, order_no):
        url = self.card_cancel_sales_url(order_no)
        res = self._request(url)
        logger.debug("got response %s" % etree.tostring(res))
        return self._parse_response_card_xml(response_factory, res)

    def request_card_inquiry(self, response_factory, order_no):
        url = self.card_inquiry_url(order_no)
        res = self._request(url)
        logger.debug("got response %s" % etree.tostring(res))
        return self._parse_inquiry_response_card_xml(response_factory, res)

    def _request(self, url, message=None):
        content_type = "application/xhtml+xml;charset=UTF-8"
        #body = etree.tostring(message, encoding='utf-8') if message else ''
        body = etree.tostring(message) if message is not None else ''
        url_parts = urlparse.urlparse(url)

        if url_parts.scheme == "http":
            http = self._httplib.HTTPConnection(host=url_parts.hostname, port=url_parts.port, timeout=self.api_timeout)
        elif url_parts.scheme == "https":
            http = self._httplib.HTTPSConnection(host=url_parts.hostname, port=url_parts.port, timeout=self.api_timeout)
        else:
            raise ValueError, "unknown scheme %s" % (url_parts.scheme)

        headers = {
            "Content-Type": content_type,
        }

        headers.update(self.auth_header)

        logger.debug("request %s body = %s" % (url, sanitize_card_number(body)))
        try:
            http.request("POST", url_parts.path, body=body,headers=headers)
            res = http.getresponse()
            logger.debug('%(url)s %(status)s %(reason)s' % dict(
                url=url,
                status=res.status,
                reason=res.reason,
            ))
            if res.status != 200:
                raise Exception(res.reason)

            return etree.parse(res).getroot()
        except (socket.timeout, ssl.SSLError), e:
            logger.warn('multicheckout api request timeout: %s(%s)' % (type(e), e.message))
            raise MultiCheckoutAPITimeoutError(e)
        except Exception as e:
            logger.error('multicheckout api request error: %s(%s)' % (type(e), e.message))
            raise MultiCheckoutAPIError(e)
        finally:
            http.close()

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

    def _create_request_card_xml(self, card_auth, check=False, forced_3d_auth=False):
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
            self._add_param(secure_3d, 'Mvn', card_auth.Mvn, optional=forced_3d_auth)
            self._add_param(secure_3d, 'Xid', card_auth.Xid, optional=forced_3d_auth)
            self._add_param(secure_3d, 'Ts', card_auth.Ts, optional=forced_3d_auth)
            self._add_param(secure_3d, 'ECI', card_auth.ECI, optional=forced_3d_auth)
            self._add_param(secure_3d, 'CAVV', card_auth.CAVV, optional=forced_3d_auth)
            self._add_param(secure_3d, 'CavvAlgorithm', card_auth.CavvAlgorithm, optional=forced_3d_auth)
            self._add_param(secure_3d, 'CardNo', card_auth.CardNo, optional=forced_3d_auth)
        return message

    def _create_request_card_sales_part_cancel_xml(self, params):
        message = etree.Element('Message')
        sales_part_cancel = etree.SubElement(message, 'SalesPartCan')
        order = etree.SubElement(sales_part_cancel, 'Order')
        self._add_param(order, 'SalesAmountCancellation', str(params.SalesAmountCancellation))
        self._add_param(order, 'TaxCarriageCancellation', str(params.TaxCarriageCancellation))

        return message

    def _parse_response_card_xml(self, response_factory, element):
        card_response = response_factory.create_multicheckout_response_card()
        assert element.tag == "Message"
        for e in element:
            if e.tag == "Request":
                for sube in e:
                    if sube.tag == "BizClassCd":
                        card_response.BizClassCd = maybe_unicode(sube.text)
                    elif sube.tag == "Storecd":
                        card_response.Storecd = maybe_unicode(sube.text)
            if e.tag == "Result":
                for sube in e:
                    if sube.tag == "SettlementInfo":
                        for ssube in sube:
                            if ssube.tag == "OrderNo":
                                card_response.OrderNo = maybe_unicode(ssube.text)
                            elif ssube.tag == "Status":
                                card_response.Status = maybe_unicode(ssube.text)
                            elif ssube.tag == "PublicTranId":
                                card_response.PublicTranId = maybe_unicode(ssube.text)
                            elif ssube.tag == "AheadComCd":
                                card_response.AheadComCd = maybe_unicode(ssube.text)
                            elif ssube.tag == "ApprovalNo":
                                card_response.ApprovalNo = maybe_unicode(ssube.text)
                            elif ssube.tag == "CardErrorCd":
                                card_response.CardErrorCd = maybe_unicode(ssube.text)
                            elif ssube.tag == "ReqYmd":
                                card_response.ReqYmd = maybe_unicode(ssube.text)
                            elif ssube.tag == "CmnErrorCd":
                                card_response.CmnErrorCd = maybe_unicode(ssube.text)
        return card_response

    def _parse_inquiry_response_card_xml(self, response_factory, element):
        inquiry_card_response = response_factory.create_multicheckout_inquiry_response_card()
        assert element.tag == "Message"
        for e in element:
            if e.tag == "Request":
                for sube in e:
                    if sube.tag == "Storecd":
                        inquiry_card_response.Storecd = maybe_unicode(sube.text)
            if e.tag == "Result":
                for sube in e:
                    if sube.tag == "Info":
                        for ssube in sube:
                            if ssube.tag == "EventDate":
                                inquiry_card_response.EventDate = maybe_unicode(ssube.text)
                            elif ssube.tag == "Status":
                                inquiry_card_response.Status = maybe_unicode(ssube.text)
                            elif ssube.tag == "CardErrorCd":
                                inquiry_card_response.CardErrorCd = maybe_unicode(ssube.text)
                            elif ssube.tag == "ApprovalNo":
                                inquiry_card_response.ApprovalNo = maybe_unicode(ssube.text)
                            elif ssube.tag == "CmnErrorCd":
                                inquiry_card_response.CmnErrorCd = maybe_unicode(ssube.text)
                    elif sube.tag == "Order":
                        for ssube in sube:
                            if ssube.tag == "OrderNo":
                                inquiry_card_response.OrderNo = maybe_unicode(ssube.text)
                            elif ssube.tag == "ItemName":
                                inquiry_card_response.ItemName = maybe_unicode(ssube.text)
                            elif ssube.tag == "OrderYMD":
                                inquiry_card_response.OrderYMD = maybe_unicode(ssube.text)
                            elif ssube.tag == "SalesAmount":
                                inquiry_card_response.SalesAmount = maybe_unicode(ssube.text)
                            elif ssube.tag == "FreeData":
                                inquiry_card_response.FreeData = maybe_unicode(ssube.text)
                    elif sube.tag == "ClientInfo":
                        for ssube in sube:
                            if ssube.tag == "ClientName":
                                inquiry_card_response.ClientName = maybe_unicode(ssube.text)
                            elif ssube.tag == "MailAddress":
                                inquiry_card_response.MailAddress = maybe_unicode(ssube.text)
                            elif ssube.tag == "MailSend":
                                inquiry_card_response.MailSend = maybe_unicode(ssube.text)
                    elif sube.tag == "CardInfo":
                        for ssube in sube:
                            if ssube.tag == "CardNo":
                                inquiry_card_response.CardNo = maybe_unicode(ssube.text)
                            elif ssube.tag == "CardLimit":
                                inquiry_card_response.CardLimit = maybe_unicode(ssube.text)
                            elif ssube.tag == "CardHolderName":
                                inquiry_card_response.CardHolderName = maybe_unicode(ssube.text)
                            elif ssube.tag == "PayKindCd":
                                inquiry_card_response.PayKindCd = maybe_unicode(ssube.text)
                            elif ssube.tag == "PayCount":
                                inquiry_card_response.PayCount = maybe_unicode(ssube.text)
                            elif ssube.tag == "SecureKind":
                                inquiry_card_response.SecureKind = maybe_unicode(ssube.text)
                    elif sube.tag == "History":
                        history = response_factory.create_multicheckout_inquiry_response_card_history()
                        history.inquiry = inquiry_card_response
                        for ssube in sube:
                            if ssube.tag == "BizClassCd":
                                history.BizClassCd = maybe_unicode(ssube.text)
                            elif ssube.tag == "EventDate":
                                history.EventDate = maybe_unicode(ssube.text)
                            elif ssube.tag == "SalesAmount":
                                history.SalesAmount = maybe_unicode(ssube.text)

        return inquiry_card_response

    def _parse_secure3d_enrol_response(self, response_factory, element):
        enrol_response = response_factory.create_secure3d_req_enrol_response()
        assert element.tag == "Message"
        for e in element:
            if e.tag == 'Md':
                enrol_response.Md = maybe_unicode(e.text)
            elif e.tag == 'ErrorCd':
                enrol_response.ErrorCd = maybe_unicode(e.text)
            elif e.tag == 'RetCd':
                enrol_response.RetCd = maybe_unicode(e.text)
            elif e.tag == 'AcsUrl':
                enrol_response.AcsUrl = maybe_unicode(e.text)
            elif e.tag == 'PaReq':
                enrol_response.PaReq = maybe_unicode(e.text)
        return enrol_response

    def _parse_secure3d_auth_response(self, response_factory, element):
        auth_response = response_factory.create_secure3d_auth_response()
        assert element.tag == "Message"
        for e in element:
            if e.tag == 'ErrorCd':
                auth_response.ErrorCd = maybe_unicode(e.text)
            elif e.tag == 'RetCd':
                auth_response.RetCd = maybe_unicode(e.text)
            elif e.tag == 'Xid':
                auth_response.Xid = maybe_unicode(e.text)
            elif e.tag == 'Ts':
                auth_response.Ts = maybe_unicode(e.text)
            elif e.tag == 'Cavva':
                auth_response.Cavva = maybe_unicode(e.text)
            elif e.tag == 'Cavv':
                auth_response.Cavv = maybe_unicode(e.text)
            elif e.tag == 'Eci':
                auth_response.Eci = maybe_unicode(e.text)
            elif e.tag == 'Mvn':
                auth_response.Mvn = maybe_unicode(e.text)
        return auth_response

