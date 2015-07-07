# encoding: utf-8
from webhelpers.paginate import PageURL_WebOb, Page
import logging

logger = logging.getLogger(__name__)

class Helpers(object):
    def __init__(self, request):
        self.request = request

    def test_helper(self):
        return u'test'

class ViewHelpers(object):
    def get_date(self, datetime):
        return "{0:%Y-%m-%d}".format(datetime)

    def get_time(self, datetime):
        return "{0:%H:%M}".format(datetime)

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
    def format_datetime(cls, datetime):
        if datetime:
            return datetime.strftime("%Y/%m/%d %H:%M")
        else:
            return ""

    @classmethod
    def format_date(cls, datetime):
        if datetime:
            return datetime.strftime("%Y/%m/%d")
        else:
            return ""
