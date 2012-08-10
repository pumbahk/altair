# -*- coding: utf-8 -*-
import os
from unittest import TestCase

from . import xls_export

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../templates/reports/")


class SalesScheduleReportExporterTestCase(TestCase):
    def setUp(self):
        self.template_path = os.path.join(TEMPLATE_DIR, 'sales_schedule_report_template.xls')

    def testOk(self):
        exporter = xls_export.SalesScheduleReportExporter(template=self.template_path)
        sheet1 = exporter.add_sheet(u"追加1")
        sheet2 = exporter.add_sheet(u"追加2")
        exporter.remove_sheet(0)
        exporter.remove_sheet(0)
        result = exporter.as_string()
        self.assertTrue(len(result) > 0)


class SeatAssignExporterTestCase(TestCase):
    def setUp(self):
        self.template_path = os.path.join(TEMPLATE_DIR, 'assign_template.xls')

    def testOk(self):
        exporter = xls_export.SeatAssignExporter(template=self.template_path)
        org_sheet = exporter.workbook.get_sheet(0)
        org_sheet.name = u'テンプレートのシート'
        exporter.add_records(org_sheet, {
            'records': [
                {
                    'block': u'１階',
                    'line': "2",
                    'stocks': ["A1", u"〜", "B2", "10"],
                },
                {
                    'block': u'１階',
                    'line': "4",
                    'returns': ["44", u"〜", "44", "1/10", "1"],
                },
            ],
            'total1': "2",
            'total2': "10",
            'seattype': u"■Ｓ席",
        })
        
        test_sheet = exporter.add_sheet(u"テスト")
        exporter.add_records(test_sheet, {
            'records': [
                {'block': u'１階'},
                {'block': u'アリーナ'},
            ],
        })
        exporter.add_records(test_sheet, {
            'records': [
                {'block': u'２階'},
            ],
        })
        exporter.set_id(test_sheet, "CTDLM08230")
        exporter.set_datetime(test_sheet, u"2012 年 7 月 24 日 (火)")
        exporter.set_event_name(test_sheet, u"テストイベント名")
        exporter.set_performance_datetime(test_sheet, u"2011年08月23日18時30分")
        exporter.set_performance_name(test_sheet, u"三重県営サンアリーナ")
        result = exporter.as_string()
        self.assertTrue(len(result) > 0)

    def testAddSheet(self):
        exporter = xls_export.SeatAssignExporter(template=self.template_path)
        sheet = exporter.add_sheet(u"テスト")
        sheets = exporter.get_sheets()
        self.assertEqual(len(sheets), 2)
