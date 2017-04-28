# -*- coding: utf-8 -*-
import os
import shutil
import urllib
import glob
import xlrd, xlwt
from altair.app.ticketing.orders.models import Order
from altair.app.ticketing.core.models import TicketPrintHistory
from pyramid.response import FileResponse
from xlutils.copy import copy
from datetime import datetime
from altair.sqlahelper import get_db_session
from xlwt import Workbook, Font, Alignment, Borders, Pattern, Protection, Formula, XFStyle
import sqlahelper

DBSession = sqlahelper.get_session()


class ReservationReportOperator:
    def __init__(self, request, order, user):
        self.__request = request
        self.__var_dir = request.registry.settings.get('reservation.var_dir', False)
        self.__user = user
        self.__slave_session = get_db_session(request, name="slave")
        self.__file_name = self.create_file_name()
        self.__order = order

    def get_slave_session(self):
        return self.__slave_session

    def get_var_dir(self):
        return self.__var_dir

    def get_file_name(self):
        return self.__file_name

    def get_order(self):
        return self.__order

    def get_user(self):
        return self.__user

    def create_file_name(self):
        now = datetime.now()
        order_count = self.get_slave_session().query(Order).filter(Order.operator_id == self.get_user().id).count()
        file_name = u"{0}_{1}_{2:05d}.xls".format(self.get_user().name, now.strftime("%Y%m%d"), order_count).encode('utf-8')
        return file_name

    @property
    def template_file_path(self):
        template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../templates/orders")
        template_file = "{0}/{1}".format(template_dir, "reservation_report.xls")
        return template_file

    @property
    def download_file_path(self):
        download_file = os.path.join("{0}{1}".format(self.get_var_dir(), self.get_file_name()))
        return download_file

    def delete_used_file(self):
        delete_files = glob.glob('{0}./*.xls'.format(self.get_var_dir()))
        for file in delete_files:
            os.remove(file)

    def copy_template_file(self):
        shutil.copyfile(self.template_file_path, self.download_file_path)

    def insert_ticket_print_history(self):
        order = self.get_order()
        for item in order.items:
            for element in item.elements:
                history = TicketPrintHistory(
                    operator_id=self.get_user().id,
                    ordered_product_item_id=element.id,
                    order_id=order.id,
                    item_token_id=element.tokens[0].id
                    )
                DBSession.add(history)
                DBSession.flush()

    def create_report_response(self):
        # 前回のファイルを削除(オペレータごと)
        self.delete_used_file()

        # ワークディレクトリにコピー
        self.copy_template_file()

        writer = ReservationReportWriter(self.download_file_path, self.get_order(), self.get_user())
        writer.write()

        self.get_order().mark_issued_or_printed(issued=True)

        # 発券作業者を埋める
        self.insert_ticket_print_history()

        response = FileResponse(os.path.abspath(self.download_file_path))
        response.headers = [
            ('Content-Type', 'application/octet-stream; charset=utf-8'),
            ('Content-Disposition', "attachment; filename*=utf-8''%s" % urllib.quote(self.get_file_name()))
        ]
        return response


class ReservationReportWriter:
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

    @classmethod
    def get_date_style(cls):
        font_title = Font()
        font_title.name = u"ＭＳ Ｐゴシック"
        font_title.height = 12 * 30

        c_border = xlwt.Borders()
        c_border.bottom = xlwt.Borders.THIN

        c_style = xlwt.XFStyle()
        c_style.borders = c_border
        c_style.font = font_title
        return c_style

    @classmethod
    def get_performance_style(cls):
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

    @classmethod
    def get_goods_style(cls):
        font_title = Font()
        font_title.name = u"ＭＳ Ｐゴシック"
        font_title.height = 7 * 25

        c_border = xlwt.Borders()
        c_border.bottom = xlwt.Borders.THIN
        c_border.left = xlwt.Borders.THIN
        c_border.top = xlwt.Borders.THIN

        c_style = xlwt.XFStyle()
        c_style.borders = c_border
        c_style.font = font_title
        return c_style

    @classmethod
    def get_goods_num_style(cls):
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

    @classmethod
    def get_sum_quantity_style(cls):
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

    @classmethod
    def get_footer_style(cls):
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
            sheet.write(row + num, 8, item.quantity, self.get_goods_num_style())

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
