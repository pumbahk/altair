# -*- coding:utf-8 -*-

""" TBA
"""

from xml.etree import ElementTree as etree
import httplib
from . import models as m

class Checkout3D(object):
    def __init__(self, auth_id, auth_password, shop_code, api_base_url):
        self.auth_id = auth_id
        self.auth_password = auth_password
        self.shop_code = shop_code
        self.api_base_url = api_base_url

    @property
    def auth_header(self):
        return "Authorization: Basic " + (self.auth_id + ":" + self.auth_password).encode('base64').strip()

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

    def card_sales_cancel_url(self, order_no):
        return self.api_url + "/card/OrderNo/%(order_no)s/SalesCan" % dict(order_no=order_no)

    def card_inquiry_url(self, order_no):
        return self.api_url + "/card/OrderNo/%(order_no)s" % dict(order_no=order_no)


    def request_card_check(self, order_no, card_auth):
        message = self._create_request_card_xml(card_auth, check=True)
        url = self.card_check_url(order_no)
        content_type = "application/xhtml+xml;charset=UTF-8"

    @property
    def api_url(self):
        return self.api_base_url.rstrip('/') + '/'  + self.shop_code.lstrip('/')

    def _add_param(self, parent, name, value, optional=False):

        if not value:
            if optional:
                return None
            else:
                raise ValueError, name
        e = etree.SubElement(parent, name)
        e.text = value
        return e

    def _create_request_card_xml(self, card_auth, check=False):
        """
        :param card_auth: :class:`.models.MultiCheckoutRequestCard`

        """

        # メッセージタグ <Message>
        message = etree.Element('<Message>')

        # オーソリ情報 <Message><Auth>
        auth = etree.SubElement(message, 'Auth')

        # 注文情報 <Message><Auth><Order>
        order = etree.SubElement(auth, 'Order')
        # 商品コード
        self._add_param(order, 'ItemCd', card_auth.ItemCd, optional=True)
        self._add_param(order, 'ItemName', card_auth.ItemName, optional=True)
        self._add_param(order, 'OrderYMD', card_auth.OrderYMD, optional=check)
        self._add_param(order, 'SalesAmount', card_auth.SalesAmount, optional=check)
        self._add_param(order, 'TaxCarriage', card_auth.TaxCarriage, optional=True)
        self._add_param(order, 'FreeData', card_auth.FreeData, optional=True)
        self._add_param(order, 'ClientName', card_auth.ClientName, optional=check)
        self._add_param(order, 'MailAddress', card_auth.MailAddress, optional=card_auth.MailSend=='1')
        self._add_param(order, 'MailSend', card_auth.MailSend)


        # カード情報 <Message><Auth><Card>
        card = etree.SubElement(message, 'Card')
        self._add_param(card, 'CardNo', card_auth.CardNo)
        self._add_param(card, 'CardLimit', card_auth.CardLimit)
        self._add_param(card, 'CardHolderName', card_auth.CardHolderName, optional=check)
        self._add_param(card, 'PayKindCd', card_auth.PayKindCd, optional=check)
        self._add_param(card, 'PayCount', card_auth.PayCount)
        self._add_param(card, 'SecureKind', card_auth.SecureKind)

        # CVVチェック
        secure_code = etree.SubElement(message, 'SecureCode')
        self._add_param(secure_code, 'Code', card_auth.SecureCode, optional=card_auth.SecureKind != '2')

        # セキュア3D
        secure_3d = etree.SubElement(message, 'Secure3D')
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