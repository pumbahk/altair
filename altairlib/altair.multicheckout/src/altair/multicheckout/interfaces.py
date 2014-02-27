# -*- coding:utf-8 -*-

""" TBA
"""
from zope.interface import Interface, Attribute

class IMultiCheckout(Interface):
    def request_card_check(order_no, card_auth):
        """ 
        """
        
    def request_card_auth(order_no, card_auth):
        """ 
        """

    def request_card_cancel_auth(order_no, card_auth):
        """ 
        """

    def request_card_sales(order_no, card_auth):
        """ 
        """

    def request_card_cancel_sales(order_no, card_auth):
        """ 
        """

    def request_card_inquiry(order_no, card_auth):
        """ 
        """

class ICardBrandDetecter(Interface):
    def __call__(card_number):
        """
        :return: str of brand symbol
        """

class ICancelFilter(Interface):
    def is_cancelable(order_no):
        """ checkf for cancelable """


class IMulticheckoutSetting(Interface):
    shop_name = Attribute(u"マルチチェックアウト店舗名")
    shop_id = Attribute(u"店舗コード")
    auth_id = Attribute(u"API 認証ID")
    auth_password = Attribute(u"API 認証パスワード")

class IMulticheckoutSettingFactory(Interface):
    def __call__(request, override_name):
        """ get IMultiChekoutSetting """

class IMulticheckoutSettingListFactory(Interface):
    def __call__(request):
        """ get list of IMultiChekoutSetting """


class IMulticheckoutImplFactory(Interface):
    def __call__(request, override_name):
        pass

class IMulticheckoutResponseFactory(Interface):
    def create_create_multicheckout_response_card():
        pass

    def create_multicheckout_inquery_response_card():
        pass

    def create_secure3d_req_enrol_response():
        pass

    def create_secure3d_auth_response():
        pass

    def create_multicheckout_inquiry_response_card_history():
        pass

class IMulticheckout3DAPI(Interface):
    def secure3d_enrol(self, order_no, card_number, exp_year, exp_month, total_amount):
        pass

    def secure3d_auth(order_no, pares, md):
        pass

    def checkout_auth_secure3d(order_no, item_name, amount, tax, client_name, mail_address, card_no, card_limit, card_holder_name, mvn, xid, ts, eci, cavv, cavv_algorithm, free_data, item_cod, date):
        pass

    def checkout_sales(order_no):
        pass

    def checkout_auth_cancel(order_no):
        pass

    def checkout_sales_different_amount(order_no, different_amount):
        pass

    def checkout_sales_part_cancel(order_no, sales_amount_cancellation, tax_carriage_cancellation):
        pass

    def checkout_sales_cancel(order_no):
        pass

    def checkout_inquiry(order_no):
        pass

    def checkout_auth_secure_code(order_no, item_name, amount, tax, client_name, mail_address, card_no, card_limit, card_holder_name, secure_code, free_data=None, item_cd=None):
        pass

