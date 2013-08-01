# -*- coding:utf-8 -*-

import unittest
from altair.app.ticketing.testing import (
    _setup_db,
    _teardown_db,
)


class LotEntryReportSettingTests(unittest.TestCase):

    def setUp(self):
        self.session = _setup_db(modules=[
            "altair.app.ticketing.core.models",
            "altair.app.ticketing.lots.models",
            "altair.app.ticketing.events.lots.models",
        ])

    def tearDown(self):
        _teardown_db()


    def _getTarget(self):
        from ..models import LotEntryReportSetting
        return LotEntryReportSetting

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _add_setting(self, frequency=0, period=0, time="", **kwargs):
        from altair.app.ticketing.core.models import Event
        from altair.app.ticketing.lots.models import Lot

        event = Event()
        lot = Lot(event=event)
        d = self._makeOne(frequency=frequency, period=period, time=time,
                          event=event,
                          lot=lot,
                          **kwargs)
        self.session.add(d)
        self.session.flush()
        return d

    def test_query_in_term_empty(self):
        from datetime import datetime
        target = self._getTarget()
        result = target.query_in_term(datetime(2013, 1, 1, 10))

        self.assertEqual(result.count(), 0)

    def test_query_in_term_no_condition(self):
        """ 無条件 """
        from datetime import datetime
        target = self._getTarget()
        self._add_setting(time="10")
        result = target.query_in_term(datetime(2013, 1, 1, 10))

        self.assertEqual(result.count(), 1)

    def test_query_in_term_started(self):
        """ 指定開始日時後 """
        from datetime import datetime
        target = self._getTarget()
        self._add_setting(time="10",
                          start_on=datetime(2012, 12, 31))
        result = target.query_in_term(datetime(2013, 1, 1, 10))

        self.assertEqual(result.count(), 1)

    def test_query_in_term_instarted(self):
        """ 指定開始日時前 """
        from datetime import datetime
        target = self._getTarget()
        self._add_setting(time="10",
                          start_on=datetime(2013, 1, 2))
        result = target.query_in_term(datetime(2013, 1, 1, 10))

        self.assertEqual(result.count(), 0)

    def test_query_in_term_infinished(self):
        """ 指定終了日時前 """
        from datetime import datetime
        target = self._getTarget()
        self._add_setting(time="10",
                          end_on=datetime(2013, 1, 2))
        result = target.query_in_term(datetime(2013, 1, 1, 10))

        self.assertEqual(result.count(), 1)

    def test_query_in_term_finished(self):
        """ 指定終了日時後 """
        from datetime import datetime
        target = self._getTarget()
        self._add_setting(time="10",
                          end_on=datetime(2012, 12, 31))
        result = target.query_in_term(datetime(2013, 1, 1, 10))

        self.assertEqual(result.count(), 0)

    def test_query_in_term_weekday(self):
        """ 指定曜日 """
        from datetime import datetime
        target = self._getTarget()
        self._add_setting(time="10",
                          day_of_week=datetime(2013, 1, 1).isoweekday())
        result = target.query_in_term(datetime(2013, 1, 8, 10))

        self.assertEqual(result.count(), 1)

    def test_query_in_term_otherday(self):
        """ 指定曜日以外 """
        from datetime import datetime
        target = self._getTarget()
        self._add_setting(time="10",
                          day_of_week=datetime(2013, 1, 7).isoweekday())
        result = target.query_in_term(datetime(2013, 1, 8, 10))

        self.assertEqual(result.count(), 0)

    def test_query_in_term_all_cond(self):
        """ 指定期間内指定曜日 """
        from datetime import datetime
        target = self._getTarget()
        self._add_setting(time="10",
                          start_on=datetime(2012, 12, 31),
                          end_on=datetime(2013, 1, 9),
                          day_of_week=datetime(2013, 1, 1).isoweekday())
        result = target.query_in_term(datetime(2013, 1, 8, 10))

        self.assertEqual(result.count(), 1)

    def test_query_reporting_about_empty(self):
        """ """
        from altair.app.ticketing.core.models import ReportFrequencyEnum

        target = self._getTarget()
        time = "10"
        frequency = ReportFrequencyEnum.Daily.v[0]
        result = target.query_reporting_about(time=time, frequency=frequency)

        self.assertEqual(result.count(), 0)

    def test_query_reporting_about_frequency_time_matched(self):
        """ """
        
        from altair.app.ticketing.core.models import ReportFrequencyEnum

        target = self._getTarget()
        time = "10"
        frequency = ReportFrequencyEnum.Daily.v[0]
        self._add_setting(time=time,
                          frequency=frequency)

        result = target.query_reporting_about(time=time, frequency=frequency)

        self.assertEqual(result.count(), 1)

    def test_query_reporting_about_frequency_time_non_matched(self):
        """ """
        
        from altair.app.ticketing.core.models import ReportFrequencyEnum

        target = self._getTarget()
        time = "10"
        frequency = ReportFrequencyEnum.Daily.v[0]
        self._add_setting(time="11",
                          frequency=frequency)

        result = target.query_reporting_about(time=time, frequency=frequency)

        self.assertEqual(result.count(), 0)

    def test_query_reporting_about_event(self):
        """ """
        
        from altair.app.ticketing.core.models import ReportFrequencyEnum

        target = self._getTarget()
        time = "10"
        frequency = ReportFrequencyEnum.Daily.v[0]
        setting = self._add_setting(time=time,
                                    frequency=frequency)

        result = target.query_reporting_about(time=time, frequency=frequency,
                                              event_id=setting.event.id)

        self.assertEqual(result.count(), 1)

    def test_query_reporting_about_no_event(self):
        """ """
        
        from altair.app.ticketing.core.models import ReportFrequencyEnum

        target = self._getTarget()
        time = "10"
        frequency = ReportFrequencyEnum.Daily.v[0]
        setting = self._add_setting(time=time,
                                    frequency=frequency)

        result = target.query_reporting_about(time=time, frequency=frequency,
                                              event_id=setting.event.id + 99999999)

        self.assertEqual(result.count(), 0)

    def test_query_reporting_about_lot(self):
        """ """
        
        from altair.app.ticketing.core.models import ReportFrequencyEnum

        target = self._getTarget()
        time = "10"
        frequency = ReportFrequencyEnum.Daily.v[0]
        setting = self._add_setting(time=time,
                                    frequency=frequency)

        result = target.query_reporting_about(time=time, frequency=frequency,
                                              lot_id=setting.lot.id)

        self.assertEqual(result.count(), 1)

    def test_query_reporting_about_no_lot(self):
        """ """
        
        from altair.app.ticketing.core.models import ReportFrequencyEnum

        target = self._getTarget()
        time = "10"
        frequency = ReportFrequencyEnum.Daily.v[0]
        setting = self._add_setting(time=time,
                                    frequency=frequency)

        result = target.query_reporting_about(time=time, frequency=frequency,
                                              lot_id=setting.lot.id + 898989898)

        self.assertEqual(result.count(), 0)

    def test_query_reporting_about_weekday(self):
        """ """
        from datetime import datetime
        from altair.app.ticketing.core.models import ReportFrequencyEnum

        target = self._getTarget()
        time = "10"
        frequency = ReportFrequencyEnum.Weekly.v[0]
        day_of_week = datetime(2013, 1, 1).isoweekday()        
        setting = self._add_setting(time=time,
                                    day_of_week=day_of_week,
                                    frequency=frequency)

        result = target.query_reporting_about(time=time, frequency=frequency,
                                              day_of_week=setting.day_of_week)
                                     

        self.assertEqual(result.count(), 1)

    def test_query_reporting_about_no_weekday(self):
        """ """
        from datetime import datetime
        from altair.app.ticketing.core.models import ReportFrequencyEnum

        target = self._getTarget()
        time = "10"
        frequency = ReportFrequencyEnum.Weekly.v[0]
        day_of_week = datetime(2013, 1, 1).isoweekday()        
        setting = self._add_setting(time=time,
                                    day_of_week=day_of_week,
                                    frequency=frequency)

        result = target.query_reporting_about(time=time, frequency=frequency,
                                              day_of_week=setting.day_of_week+1)
                                     

        self.assertEqual(result.count(), 0)

    def test_query_reporting_about_event_lot_weekday(self):
        """ """
        from datetime import datetime
        from altair.app.ticketing.core.models import ReportFrequencyEnum

        target = self._getTarget()
        time = "10"
        frequency = ReportFrequencyEnum.Weekly.v[0]
        day_of_week = datetime(2013, 1, 1).isoweekday()        
        setting = self._add_setting(time=time,
                                    day_of_week=day_of_week,
                                    frequency=frequency)

        result = target.query_reporting_about(time=time, frequency=frequency,
                                              event_id=setting.event_id,
                                              lot_id=setting.lot.id,
                                              day_of_week=setting.day_of_week)

        self.assertEqual(result.count(), 1)
