# -*- coding:utf-8 -*-

""" TBA
"""

from xml.etree import ElementTree as etree

class Checkout3D(object):
    def __init__(self, auth_id, auth_password, shop_code, api_base_url):
        self.auth_id = auth_id
        self.auth_password = auth_password
        self.shop_code = shop_code
        self.api_base_url = api_base_url


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
        区分 内容
1 2 3
認証なし セキュリティコード 3D セキュア
SSL CVV 3D
        """

        # メッセージタグ <Message>
        message = etree.Element('<Message>')

        # オーソリ情報 <Message><Auth>
        auth = etree.SubElement(message, 'Auth')

        # 注文情報 <Message><Auth><Order>
        order = etree.SubElement(auth, 'Order')
        # 商品コード
        self._add_param(order, 'ItemCD', card_auth.ItemCD, optional=True)
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

