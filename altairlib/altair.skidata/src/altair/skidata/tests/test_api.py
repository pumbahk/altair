# coding=utf-8
from datetime import datetime

from altair.skidata.api import make_whitelist, make_event_ts_property, make_blacklist
from altair.skidata.marshaller import SkidataXmlMarshaller
from altair.skidata.models import TSOption, TSAction, WhitelistRecord, Permission, TSProperty, EventTSProperty, \
    BlockingReason, BlacklistRecord, BlockingWhitelistRecord
from altair.skidata.tests.tests import SkidataBaseTest


class SkidataXmlModelTest(SkidataBaseTest):
    def setUp(self):
        # Start date and time of a Skidata event
        self.start_date = datetime(2020, 8, 5, 12, 30, 0)
        # Skidata event ID ->
        # ORG short code + start date and time of the event with a format of `YYYYmmddHHMM`
        self.event_id = 'RE{start_date}'.format(start_date=self.start_date.strftime('%Y%m%d%H%M'))

        self.ts_option = TSOption(
            order_no='RE0000000001',
            open_date=datetime(2020, 8, 5, 11, 0, 0),
            start_date=self.start_date,
            stock_type=u'1塁側指定席',
            product_name=u'1塁側指定席',
            product_item_name=u'1塁側指定席',
            gate='GATE A',
            seat_name=u'指定席',
            sales_segment=u'一般発売',
            ticket_type=0,
            person_category=1,
            event=self.event_id
        )

        self.qr_code = '97SEJPEMBI8IH134859255T5Q'

    @staticmethod
    def _print_xml(model):
        print(SkidataXmlMarshaller.marshal(model, encoding='utf-8', pretty_print=True).decode('utf-8'))

    def test_make_event_setup(self):
        # event expire is the end of the year when the skidata event starts
        expire = datetime(year=self.start_date.year, month=12, day=31, hour=23, minute=59, second=59)

        event_ts_property = make_event_ts_property(
            action=TSAction.INSERT,
            event_id=self.event_id,
            name=u'東北楽天ゴールデンイーグルス vs 北海道日本ハムファイターズ',
            expire=expire,
            start_date_or_time=self.start_date.date()
        )

        # self._print_xml(event_ts_property)

        self.assertTrue(isinstance(event_ts_property, EventTSProperty))

    def test_make_whitelist_for_insert(self):
        # whitelist expire is the end of the year when the skidata event starts
        expire = datetime(year=self.start_date.year, month=12, day=31, hour=23, minute=59, second=59)

        whitelist = make_whitelist(action=TSAction.INSERT,
                                   qr_code=self.qr_code,
                                   ts_option=self.ts_option,
                                   expire=expire)

        # self._print_xml(whitelist)

        self.assertTrue(isinstance(whitelist, WhitelistRecord))
        self.assertTrue(isinstance(whitelist.permission(), Permission))

        for ts_property in whitelist.permission().ts_property():
            self.assertTrue(isinstance(ts_property, TSProperty))

    def test_make_whitelist_for_update(self):
        # UPDATE requires the existing data
        ts_option_for_update = TSOption(ticket_type=1)
        whitelist = make_whitelist(action=TSAction.UPDATE,
                                   qr_code=self.qr_code,
                                   ts_option=ts_option_for_update)

        # self._print_xml(whitelist)

        self.assertTrue(isinstance(whitelist, WhitelistRecord))
        self.assertTrue(isinstance(whitelist.permission(), Permission))
        self.assertTrue(isinstance(whitelist.permission().ts_property(), TSProperty))

    def test_make_whitelist_for_delete(self):
        whitelist = make_whitelist(action=TSAction.DELETE, qr_code=self.qr_code)

        # self._print_xml(whitelist)

        self.assertTrue(isinstance(whitelist, WhitelistRecord))
        self.assertIsNone(whitelist.permission())

    def test_make_blacklist_for_insert(self):
        # blacklist expire is the end of the current year
        expire = datetime(year=datetime.now().year, month=12, day=31, hour=23, minute=59, second=59)

        blacklist = make_blacklist(action=TSAction.INSERT,
                                   qr_code=self.qr_code,
                                   blocking_reason=BlockingReason.CANCELED,
                                   expire=expire)

        # self._print_xml(blacklist)

        self.assertTrue(isinstance(blacklist, BlacklistRecord))
        self.assertTrue(isinstance(blacklist.blocking_whitelist(), BlockingWhitelistRecord))
        self.assertTrue(isinstance(blacklist.blocking_whitelist().permission(), Permission))

    def test_make_blacklist_for_delete(self):
        blacklist = make_blacklist(action=TSAction.DELETE,
                                   qr_code=self.qr_code,
                                   blocking_reason=BlockingReason.CANCELED)

        # self._print_xml(blacklist)

        self.assertTrue(isinstance(blacklist, BlacklistRecord))
        self.assertTrue(isinstance(blacklist.blocking_whitelist(), BlockingWhitelistRecord))
        self.assertTrue(isinstance(blacklist.blocking_whitelist().permission(), Permission))
