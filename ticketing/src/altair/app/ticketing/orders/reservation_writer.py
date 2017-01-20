# -*- coding: utf-8 -*-
# 書き換え
from datetime import datetime
import xlrd, xlwt
from xlwt import Workbook, Font, Alignment, Borders, Pattern, Protection, Formula, XFStyle
from xlutils.copy import copy


class ReservationReportWriter():
    def __init__(self, work_file, order, user):
        self.__work_file = work_file
        self.__order = order
        self.__user = user

    def get_work_file(self):
        return self.__work_file

    def get_order(self):
        return self.__order

    def get_user(self):
        return self.__user

    def get_date_style(self):
        font_title = Font()
        font_title.name = u"ＭＳ Ｐゴシック"
        font_title.height = 12 * 30

        c_border = xlwt.Borders()
        c_border.bottom = xlwt.Borders.THIN

        c_style = xlwt.XFStyle()
        c_style.borders = c_border
        c_style.font = font_title
        return c_style

    def get_performance_style(self):
        font_title = Font()
        font_title.name = u"ＭＳ Ｐゴシック"
        font_title.height = 12 * 25

        c_border = xlwt.Borders()
        c_border.bottom = xlwt.Borders.MEDIUM
        c_border.top = xlwt.Borders.MEDIUM

        c_style = xlwt.XFStyle()
        c_style.borders = c_border
        c_style.font = font_title
        return c_style

    def get_goods_style(self):
        font_title = Font()
        font_title.name = u"ＭＳ Ｐゴシック"
        font_title.height = 12 * 25

        c_border = xlwt.Borders()
        c_border.bottom = xlwt.Borders.THIN
        c_border.left = xlwt.Borders.THIN
        c_border.top = xlwt.Borders.THIN

        c_style = xlwt.XFStyle()
        c_style.borders = c_border
        c_style.font = font_title
        return c_style

    def get_sum_quantity_style(self):
        font_title = Font()
        font_title.name = u"ＭＳ Ｐゴシック"
        font_title.height = 12 * 25

        c_border = xlwt.Borders()
        c_border.top = xlwt.Borders.THIN
        c_border.left = xlwt.Borders.THIN
        c_border.right = xlwt.Borders.THIN
        c_border.bottom = xlwt.Borders.MEDIUM

        c_style = xlwt.XFStyle()
        c_style.borders = c_border
        c_style.font = font_title
        return c_style

    def get_footer_style(self):
        font_title = Font()
        font_title.name = u"ＭＳ Ｐゴシック"
        font_title.height = 12 * 30

        c_style = xlwt.XFStyle()
        c_style.font = font_title
        return c_style

    def write_date(self, sheet):
        today = datetime.now()
        sheet.write(1, 8, today.strftime("%Y/%m/%d"), self.get_date_style())

    def write_performance(self, sheet):
        sheet.write(5, 2, self.__order.performance.name, self.get_performance_style())

    def write_goods(self, sheet, products):
        row = 6
        for num, item in enumerate(products):
            # 席種・商品名
            sheet.write(row + num, 2, u"{0}・{1}".format(item.product.seat_stock_type.name, item.product.name), self.get_goods_style())
            # 枚数
            sheet.write(row + num, 8, item.quantity, self.get_goods_style())

    def write_sum_quantity(self, sheet, products):
        num = 0
        for product in products:
            num += product.quantity

        sheet.write(16, 8, num, self.get_sum_quantity_style())

    def write_order_no(self, sheet, order):
        sheet.write(44, 2, order.order_no, self.get_footer_style())

    def write_customer_name(self, sheet, order):
        shipping_address = order.shipping_address
        sheet.write(45, 2, u"{0} {1}".format(shipping_address.last_name, shipping_address.first_name), self.get_footer_style())

    def write_operator_name(self, sheet):
        sheet.write(46, 2, self.get_user().name, self.get_footer_style())

    def write(self):
        book = xlrd.open_workbook(self.__work_file, formatting_info=True)
        new_book = copy(book)
        sheet = new_book.get_sheet(1)

        order = self.get_order()
        self.write_goods(sheet, order.items)
        self.write_date(sheet)
        self.write_performance(sheet)
        self.write_order_no(sheet, order)
        self.write_customer_name(sheet, order)
        self.write_operator_name(sheet)
        self.write_sum_quantity(sheet, order.items)

        # 保存
        new_book.save(self.__work_file)
