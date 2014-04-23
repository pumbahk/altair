# -*- coding:utf-8 -*-
import unittest
from pyramid import testing
from altair.app.ticketing.testing import _setup_db, _teardown_db
from ..testing import _dummy_request, _wish

class LotEntriesTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.session = _setup_db(
            [
                "altair.app.ticketing.core.models",
                "altair.app.ticketing.lots.models",
            ]
            )

    def tearDown(self):
        testing.tearDown()
        _teardown_db()

    def _getTarget(self):
        from ..views import LotEntries
        return LotEntries

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_parse_import_file(self):
        request = testing.DummyRequest()
        context = testing.DummyResource()

        target = self._makeOne(context, request)

        f = data1.split("\n")
        result = target._parse_import_file(f)

        self.assertEqual(result, (
                        [('RT0000003109', 0), ('RT000000310A', 0)],
                        ['RT000000310B', 'RT000000310C', 'RT000000310D']
                        ))

    def test_parse_import_file_parse_error(self):
        from altair.app.ticketing.events.lots.exceptions import CSVFileParserError
        request = testing.DummyRequest()
        context = testing.DummyResource()
        target = self._makeOne(context, request)

        f = error_data1.split("\n")
        with self.assertRaises(CSVFileParserError):
            target._parse_import_file(f)

        f = error_data2.split("\n")
        with self.assertRaises(CSVFileParserError):
            target._parse_import_file(f)

        f = error_data3.split("\n")
        with self.assertRaises(CSVFileParserError):
            target._parse_import_file(f)

    def test_import_accepted_entries(self):
        from datetime import datetime
        from altair.app.ticketing.lots.models import Lot
        self.config.add_route('lots.entries.index', '/lots/entries/index')
        request = _dummy_request()
        lot = Lot(id=1, event=request.context.event)
        request.context.lot_id = 1

        wish1 = _wish(lot=lot, entry_no=u'RT0000003109', wish_order=0)
        wish2 = _wish(lot=lot, entry_no=u'RT000000310A', wish_order=0)
        wish1 = _wish(lot=lot, entry_no=u'RT000000310B', wish_order=0)
        wish1 = _wish(lot=lot, entry_no=u'RT000000310C', wish_order=0)
        wish1 = _wish(lot=lot, entry_no=u'RT000000310D', wish_order=0)
        wish3 = _wish(lot=lot, entry_no=u'RT0000000000', wish_order=0)
        wish4 = _wish(lot=lot, entry_no=u'RT0000000001', wish_order=0)
        wish5 = _wish(lot=lot, entry_no=u'RT0000000002', wish_order=0)
        # 当選
        wish6 = _wish(lot=lot, entry_no=u'RT0000000003', wish_order=0, elected_at=datetime.now())
        # 落選
        wish7 = _wish(lot=lot, entry_no=u'RT0000000004', wish_order=0, rejected_at=datetime.now())
        # キャンセル
        wish8 = _wish(lot=lot, entry_no=u'RT0000000005', wish_order=0, canceled_at=datetime.now())

        self.session.add(lot)
        self.session.flush()
        request.matchdict['lot_id'] = lot.id
        request.params['entries'] = testing.DummyResource(file=data1.split("\n"))

        target = self._makeOne(request.context, request)
        result = target.import_accepted_entries()

        self.assertEqual(result.location, 'http://example.com/lots/entries/index')
        self.assertEqual(request.session.pop_flash(),
                         [u"2件の当選予定データ、3件の落選予定データを取り込みました",
                          u"新たに2件が当選予定、3件が落選予定となりました",
                         ])

        from altair.app.ticketing.lots.models import (
            LotElectWork,
            LotRejectWork,
        )

        self.assertEqual(self.session.query(LotElectWork).filter_by(lot_entry_no='RT0000003109').count(), 1)
        self.assertEqual(self.session.query(LotElectWork).filter_by(lot_entry_no='RT000000310A').count(), 1)
        self.assertEqual(self.session.query(LotElectWork).filter_by(lot_entry_no='RT000000310B').count(), 0)
        self.assertEqual(self.session.query(LotElectWork).filter_by(lot_entry_no='RT000000310C').count(), 0)
        self.assertEqual(self.session.query(LotElectWork).filter_by(lot_entry_no='RT000000310D').count(), 0)
        self.assertEqual(self.session.query(LotElectWork).filter_by(lot_entry_no='RT0000000000').count(), 0)
        self.assertEqual(self.session.query(LotElectWork).filter_by(lot_entry_no='RT0000000001').count(), 0)
        self.assertEqual(self.session.query(LotElectWork).filter_by(lot_entry_no='RT0000000002').count(), 0)
        self.assertEqual(self.session.query(LotElectWork).filter_by(lot_entry_no='RT0000000003').count(), 0)
        self.assertEqual(self.session.query(LotElectWork).filter_by(lot_entry_no='RT0000000004').count(), 0)
        self.assertEqual(self.session.query(LotElectWork).filter_by(lot_entry_no='RT0000000005').count(), 0)

        self.assertEqual(self.session.query(LotRejectWork).filter_by(lot_entry_no='RT0000003109').count(), 0)
        self.assertEqual(self.session.query(LotRejectWork).filter_by(lot_entry_no='RT000000310A').count(), 0)
        self.assertEqual(self.session.query(LotRejectWork).filter_by(lot_entry_no='RT000000310B').count(), 1)
        self.assertEqual(self.session.query(LotRejectWork).filter_by(lot_entry_no='RT000000310C').count(), 1)
        self.assertEqual(self.session.query(LotRejectWork).filter_by(lot_entry_no='RT000000310D').count(), 1)
        self.assertEqual(self.session.query(LotRejectWork).filter_by(lot_entry_no='RT0000000000').count(), 0)
        self.assertEqual(self.session.query(LotRejectWork).filter_by(lot_entry_no='RT0000000001').count(), 0)
        self.assertEqual(self.session.query(LotRejectWork).filter_by(lot_entry_no='RT0000000002').count(), 0)
        self.assertEqual(self.session.query(LotRejectWork).filter_by(lot_entry_no='RT0000000003').count(), 0)
        self.assertEqual(self.session.query(LotRejectWork).filter_by(lot_entry_no='RT0000000004').count(), 0)
        self.assertEqual(self.session.query(LotRejectWork).filter_by(lot_entry_no='RT0000000005').count(), 0)

    def test_import_accepted_entries_not_update(self):
        from datetime import datetime
        from altair.app.ticketing.lots.models import Lot
        self.config.add_route('lots.entries.index', '/lots/entries/index')
        request = _dummy_request()
        lot = Lot(id=1, event=request.context.event)
        request.context.lot_id = 1

        # 当選
        wish6 = _wish(lot=lot, entry_no=u'RT0000000003', wish_order=0, elected_at=datetime.now())
        # 落選
        wish7 = _wish(lot=lot, entry_no=u'RT0000000004', wish_order=0, rejected_at=datetime.now())
        # キャンセル
        wish8 = _wish(lot=lot, entry_no=u'RT0000000005', wish_order=0, canceled_at=datetime.now())

        self.session.add(lot)
        self.session.flush()
        request.matchdict['lot_id'] = lot.id
        request.params['entries'] = testing.DummyResource(file=data2.split("\n"))

        target = self._makeOne(request.context, request)
        result = target.import_accepted_entries()

        self.assertEqual(result.location, 'http://example.com/lots/entries/index')
        self.assertEqual(request.session.pop_flash(),
                         [u"2件の当選予定データ、1件の落選予定データを取り込みました",
                          u"新たに0件が当選予定、0件が落選予定となりました",
                         ])

        from altair.app.ticketing.lots.models import (
            LotElectWork,
            LotRejectWork,
        )

        self.assertEqual(self.session.query(LotElectWork).filter_by(lot_entry_no='RT0000000003').count(), 0)
        self.assertEqual(self.session.query(LotElectWork).filter_by(lot_entry_no='RT0000000004').count(), 0)
        self.assertEqual(self.session.query(LotElectWork).filter_by(lot_entry_no='RT0000000005').count(), 0)

        self.assertEqual(self.session.query(LotRejectWork).filter_by(lot_entry_no='RT0000000003').count(), 0)
        self.assertEqual(self.session.query(LotRejectWork).filter_by(lot_entry_no='RT0000000004').count(), 0)
        self.assertEqual(self.session.query(LotRejectWork).filter_by(lot_entry_no='RT0000000005').count(), 0)


data1 = u"""\
状態,申し込み番号,希望順序,申し込み日,ユーザー種別,席種,枚数,イベント,会場,公演,公演コード,公演日,商品,決済方法,引取方法,配送先姓,配送先名,配送先姓(カナ),配送先名(カナ),郵便番号,国,都道府県,市区町村,住所1,住所2,電話番号1,電話番号2,FAX,メールアドレス1,メールアドレス2,姓,名,姓(カナ),名(カナ),ニックネーム,性別
当選予定,RT0000003109,1,2013-05-01 16:41,None,"抽選A席,抽選A席",4,抽選用テストイベント,博品館劇場,抽選テスト公演B,RTCHSNN0602Z,2013-06-02 15:00,抽選公演BのA席テスト,クレジットカード決済,配送,手巣戸,抽選テスト,テスト,テスト,1234567,日本国,東京都,どこか,１?２７?１６,,012345678,,,testing1@example.com,None,,,,,,
当選予定,RT000000310A,1,2013-05-01 16:42,None,"抽選A席,抽選A席",4,抽選用テストイベント,博品館劇場,抽選テスト公演B,RTCHSNN0602Z,2013-06-02 15:00,抽選公演BのA席テスト,クレジットカード決済,配送,手巣戸,抽選テスト,テスト,テスト,1234567,日本国,東京都,どこか,１?２７?１６,,012345678,,,testing2@example.com,None,,,,,,
落選予定,RT000000310B,1,2013-05-01 16:42,None,"抽選A席,抽選A席",4,抽選用テストイベント,博品館劇場,抽選テスト公演B,RTCHSNN0602Z,2013-06-02 15:00,抽選公演BのA席テスト,クレジットカード決済,配送,手巣戸,抽選テスト,テスト,テスト,1234567,日本国,東京都,どこか,１?２７?１６,,012345678,,,testing3@example.com,None,,,,,,
落選予定,RT000000310C,1,2013-05-01 16:42,None,"抽選A席,抽選A席",4,抽選用テストイベント,博品館劇場,抽選テスト公演B,RTCHSNN0602Z,2013-06-02 15:00,抽選公演BのA席テスト,クレジットカード決済,配送,手巣戸,抽選テスト,テスト,テスト,1234567,日本国,東京都,どこか,１?２７?１６,,012345678,,,testing4@example.com,None,,,,,,
落選予定,RT000000310D,1,2013-05-01 16:42,None,"抽選A席,抽選A席",4,抽選用テストイベント,博品館劇場,抽選テスト公演B,RTCHSNN0602Z,2013-06-02 15:00,抽選公演BのA席テスト,クレジットカード決済,配送,手巣戸,抽選テスト,テスト,テスト,1234567,日本国,東京都,どこか,１?２７?１６,,012345678,,,testing5@example.com,None,,,,,,
""".encode('Shift_JIS')

data2 = u"""\
状態,申し込み番号,希望順序
当選予定,u'RT0000000003,1
落選予定,u'RT0000000004,1
当選予定,u'RT0000000005,1
""".encode('Shift_JIS')

error_data1 = u"""\
状態,申し込み番号,希望順序
当選予定,RT0000003109,
""".encode('Shift_JIS')

error_data2 = u"""\
状態,申し込み番号,希望順序
当選予定,,1
""".encode('Shift_JIS')

error_data3 = u"""\
状態,申し込み番号,希望順序
,RT0000003109,1
""".encode('Shift_JIS')
