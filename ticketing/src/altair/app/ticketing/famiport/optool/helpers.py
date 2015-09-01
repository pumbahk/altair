# encoding: utf-8
from webhelpers.paginate import PageURL_WebOb, Page
import logging, locale
import json
from .api import get_famiport_shop_by_code
from ..models import FamiPortReceiptType

logger = logging.getLogger(__name__)

class Helpers(object):
    def __init__(self, request):
        self.request = request

    def json(self, v):
        return json.dumps(v, ensure_ascii=True)

class ViewHelpers(object):
    def __init__(self, request):
        self.request = request

    def get_date(self, datetime):
        return "{0:%Y-%m-%d}".format(datetime)

    def get_time(self, datetime):
        return "{0:%H:%M}".format(datetime)

    def format_date(cls, datetime, format="%Y/%m/%d"):
        if datetime:
            return datetime.strftime(format)
        else:
            return u'-'

    def format_time(cls, datetime, format="%H:%M"):
        if datetime:
            return datetime.strftime(format)
        else:
            return u'-'

    def format_datetime(cls, datetime, format="%Y/%m/%d %H:%M"):
        if datetime:
            return datetime.strftime(format)
        else:
            return u'-'

    def format_currency(self, amount):
        locale.setlocale(locale.LC_ALL, 'ja_JP.UTF-8')
        return locale.currency(amount, grouping=True).decode("UTF-8")

    def format_famiport_order_identifier(self, identifier):
        return identifier[3:12]

    def get_barcode_no_text(self, barcode_no):
        if barcode_no:
            return barcode_no
        else:
            return u'-'

    def get_famiport_shop_by_code(self, shop_code):
        return get_famiport_shop_by_code(self.request, shop_code)

    def get_shop_name_text(self, famiport_shop):
        if famiport_shop:
            return famiport_shop.name
        else:
            return u'-'

    def get_management_number_from_famiport_order_identifier(self, famiport_order_identifier):
        """
        注文IDの下9桁を取って発券管理番号を返す
        :param famiport_order_identifier:
        :return:
        """
        return famiport_order_identifier[3:12]

    def display_payment_shop_code(self, famiport_receipt):
        display_code = u'-'

        if famiport_receipt.type == FamiPortReceiptType.Payment.value or \
           famiport_receipt.type == FamiPortReceiptType.CashOnDelivery.value:
            if famiport_receipt.completed_at is not None and famiport_receipt.rescued_at is None:
                display_code = famiport_receipt.shop_code

        return display_code

    def display_delivery_shop_code(self, famiport_receipt):
        display_code = u'-'

        if famiport_receipt.type == FamiPortReceiptType.Ticketing.value or \
           famiport_receipt.type == FamiPortReceiptType.CashOnDelivery.value:
            if famiport_receipt.completed_at is not None and famiport_receipt.rescued_at is None:
                display_code = famiport_receipt.shop_code

        return display_code

    def display_payment_date(self, famiport_receipt):
        display_date = None
        if famiport_receipt.famiport_order.paid_at:
            display_date = famiport_receipt.famiport_order.paid_at
        elif famiport_receipt.completed_at is not None and famiport_receipt.rescued_at is None:
            display_date = famiport_receipt.completed_at

        return display_date

    def display_delivery_date(self, famiport_receipt):
        display_date = None
        if famiport_receipt.famiport_order.issued_at:
            display_date = famiport_receipt.famiport_order.issued_at
        elif famiport_receipt.completed_at is not None and famiport_receipt.rescued_at is None:
            display_date = famiport_receipt.completed_at

        return display_date

def get_paginator(request, query, page=1, items_per_page=20):
    page_url = PageURL_WebOb(request)
    return Page(query, page, url=page_url, items_per_page=items_per_page)

class RefundTicketSearchHelper(object):
    columns = (('refund_status', u'払戻状況'), ('district_code', u'地区'), ('refunded_branch_code', u'営業所'),
               ('issued_shop_code', u'発券店番'), ('issued_branch_name', u'発券店舗名'), ('management_number', u'管理番号'),
               ('barcode_number', u'バーコード'), ('event_code', u'興行コード'), ('event_subcode', u'興行サブコード'),
               ('performance_date', u'公演日'), ('event_name', u'興行名'),
               ('refunded_amount', u'返金額'), ('refunded_at', u'払戻日時'), ('refunded_shop_code', u'払戻店番'),
               ('refunded_branch_name', u'払戻店舗名'))

    def __init__(self, request):
        self.request = request

    @classmethod
    def get_columns(cls):
        return cls.columns

    @classmethod
    def get_refund_status_text(cls, refunded_at):
        if refunded_at:
            return u'済'
        else:
            return u'未'

    @classmethod
    def get_management_number_from_famiport_order_identifier(cls, famiport_order_identifier):
        """
        注文IDの下9桁を取って発券管理番号を返す
        :param famiport_order_identifier:
        :return:
        """
        return famiport_order_identifier[3:12]

    @classmethod
    def format_datetime(cls, datetime, format="%Y/%m/%d %H:%M"):
        if datetime:
            return datetime.strftime(format)
        else:
            return u'-'

    @classmethod
    def format_date(cls, datetime, format="%Y/%m/%d"):
        if datetime:
            return datetime.strftime(format)
        else:
            return u'-'

    def format_currency(self, amount):
        locale.setlocale(locale.LC_ALL, 'ja_JP.UTF-8')
        return locale.currency(amount, grouping=True).decode("UTF-8")

    def get_famiport_shop_by_code(self, shop_code):
        return get_famiport_shop_by_code(self.request, shop_code)

    def get_shop_name_text(self, famiport_shop):
        if famiport_shop:
            return famiport_shop.name
        else:
            return u'-'
