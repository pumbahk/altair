# -*- coding:utf-8 -*-

""" TBA
"""
from zope.interface import Interface

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
