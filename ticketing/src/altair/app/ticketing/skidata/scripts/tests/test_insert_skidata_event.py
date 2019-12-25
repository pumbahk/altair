# coding=utf-8
import sys
import unittest
from datetime import datetime

from altair.app.ticketing.skidata.scripts import insert_skidata_event
from altair.app.ticketing.skidata.scripts.tests.test_helper import create_organization, create_event, create_performance
from altair.app.ticketing.testing import _setup_db, _teardown_db
from altair.skidata.api import make_event_ts_property
from altair.skidata.models import SkidataWebServiceResponse, Error, HSHErrorType, HSHErrorNumber, TSAction
from altair.skidata.sessions import SkidataWebServiceSession
from altair.sqlahelper import register_sessionmaker_with_engine
from mock import patch, MagicMock, PropertyMock
from pyramid.testing import DummyRequest, setUp, tearDown


@patch.object(insert_skidata_event, 'skidata_webservice_session')
@patch.object(insert_skidata_event, 'bootstrap')
@patch.object(insert_skidata_event, 'setup_logging')
class InsertSkidataEventTest(unittest.TestCase):
    def setUp(self):
        self.request = DummyRequest()
        self.config = setUp(request=self.request)
        self.session = _setup_db(modules=[
            'altair.app.ticketing.core.models',
            'altair.app.ticketing.orders.models'
        ])
        org = create_organization(session=self.session, code='RE',
                                  short_name=u'楽天イーグルス', enable_skidata=True)
        event = create_event(session=self.session, organization=org,
                             title=u'2020年 プロ野球公式戦', enable_skidata=True)

        start_on = datetime(2020, 8, 1, 10, 0)
        self.base_perf = create_performance(session=self.session, event=event,
                                            name=u'楽天イーグルス vs 北海道日本ハムファイターズ',
                                            open_on=None, start_on=start_on)
        self.session.flush()

        register_sessionmaker_with_engine(self.config.registry, 'slave', self.session.bind)

    def tearDown(self):
        _teardown_db()
        tearDown()

    @staticmethod
    def _mock_skidata_behaviour(errors=None):
        skidata_resp = SkidataWebServiceResponse(status_code=200, text='')
        success_prop = PropertyMock(return_value=errors in (None, []))
        errors_prop = PropertyMock(return_value=errors or [])
        type(skidata_resp).success = success_prop
        type(skidata_resp).errors = errors_prop

        skidata_session = SkidataWebServiceSession(
            url='http://localhost/ImporterWebService', timeout=20,
            version='HSHIF25', issuer='1', receiver='1'
        )
        skidata_session.send = MagicMock(return_value=skidata_resp)
        return skidata_session, success_prop, errors_prop

    def test_insert_skidata_event(self, mock_setup_logging, mock_bootstrap, mock_skidata_session):
        """正常系テスト　SKIDATA へ EVENT を追加"""
        mock_setup_logging.return_value = None
        mock_bootstrap.return_value = {'request': self.request}

        skidata_session, success_prop, errors_prop = self._mock_skidata_behaviour()
        mock_skidata_session.return_value = skidata_session

        sys.argv = ['', '-c', 'altair.ticketing.admin.ini', '-p', str(self.base_perf.id)]
        insert_skidata_event.main()

        self.assertTrue(success_prop.call_count == 1)
        self.assertFalse(errors_prop.called)  # 成功レスポンスなのでエラー内容の確認は行われていない

        # 公演の開演年が指定（-y）の年と一致しないので連携対象の公演データは見つからない
        sys.argv = ['', '-c', 'altair.ticketing.admin.ini', '-y', str(self.base_perf.start_on.year + 1)]
        insert_skidata_event.main()

        self.assertTrue(success_prop.call_count == 1)
        self.assertFalse(errors_prop.called)  # 成功レスポンスなのでエラー内容の確認は行われていない

    def test_fail_to_insert_skidata_event(self, mock_setup_logging, mock_bootstrap, mock_skidata_session):
        """正常系テスト　SKIDATA へ EVENT を追加失敗"""
        mock_setup_logging.return_value = None
        mock_bootstrap.return_value = {'request': self.request}

        error_event = make_event_ts_property(action=TSAction.INSERT, event_id='RE202008011000',
                                             name=u'楽天イーグルス vs 北海道日本ハムファイターズ 2020/08/01',
                                             start_date_or_time=self.base_perf.start_on.date())
        errors = [
            Error(type_=HSHErrorType.ERROR, number=HSHErrorNumber.MISSING_MANDATORY_FIELD,
                  description='Missing Mandatory Field', event_ts_property=error_event)
        ]
        skidata_session, success_prop, errors_prop = self._mock_skidata_behaviour(errors=errors)
        mock_skidata_session.return_value = skidata_session

        sys.argv = ['', '-c', 'altair.ticketing.admin.ini', '-p', str(self.base_perf.id)]
        insert_skidata_event.main()

        self.assertTrue(success_prop.called)
        self.assertTrue(errors_prop.called)  # 失敗レスポンスなのでエラー内容の確認が行われている
