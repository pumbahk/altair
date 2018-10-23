# -*- coding: utf-8 -*-
import unittest
import mock

from datetime import datetime
from xml.etree import ElementTree
from pyramid import testing
from xml.dom.minidom import parseString


class GetStdOnlyTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.registry.settings = {
            'altair.point.endpoint': 'http://stg-point-api.stg.jp.local/',
            'altair.point.timeout': 20,
            'altair.point.secret_key': 'PANDA',
            'altair.point.RT.group_id': '468',
            'altair.point.RT.reason_id': '1904'
        }
        self.config.include('altair.point')

    def _callFUT(self, *args, **kwargs):
        from . import api
        # 実際に通信をする場合は以下の2行をコメントアウトしてください
        result_xml = mock.MagicMock(return_value=self.create_get_stdonly_response())
        api.get_stdonly = result_xml
        return api.get_stdonly(*args, **kwargs)

    def test_it(self):
        # easy_id 8235101の保有ポイントが取得できるか確認
        easy_id = '8235101'
        org = 'RT'

        request = testing.DummyRequest()
        result = self._callFUT(
            request=request,
            easy_id=easy_id,
            org=org
        )
        print(result)
        result_tree = ElementTree.fromstring(result)

        # 正常終了していることを確認
        result_code = result_tree.find('data').find('result_code').text
        self.assertEqual(result_code, '0')

    @staticmethod
    def create_get_stdonly_response():
        point_xml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" \
                    "<Root>" \
                    "<data>" \
                    "<easy_id>8235101</easy_id>" \
                    "<fix_point>9000</fix_point>" \
                    "<sec_able_point>9000</sec_able_point>" \
                    "<month_used_point>1000</month_used_point>" \
                    "<month_point>100000</month_point>" \
                    "<min_point>50</min_point>" \
                    "<order_max_point>30000</order_max_point>" \
                    "<res_time>2018-10-22 16:17:09</res_time>" \
                    "<result_code>0</result_code>" \
                    "</data>" \
                    "<confirmation_key>3f6b66811f54f7059dcc9ccc519504cd</confirmation_key>" \
                    "</Root>"
        dom = parseString(point_xml)
        return dom.toprettyxml()


class AuthStdOnlyTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.registry.settings = {
            'altair.point.endpoint': 'http://stg-point-api.stg.jp.local/',
            'altair.point.timeout': 20,
            'altair.point.secret_key': 'PANDA',
            'altair.point.RT.shop_name': '楽天チケットでのポイント利用',
            'altair.point.RT.group_id': '468',
            'altair.point.RT.reason_id': '1904'
        }
        self.config.include('altair.point')

    def _callFUT(self, *args, **kwargs):
        from . import api
        # 実際に通信をする場合は以下の2行をコメントアウトしてください
        result_xml = mock.MagicMock(return_value=self.create_auth_stdonly_response())
        api.auth_stdonly = result_xml
        return api.auth_stdonly(*args, **kwargs)

    def test_it(self):
        # easy_id 8235101の保有ポイントでポイント充当する
        easy_id = '8235101'
        auth_point = '100'
        req_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        org = 'RT'

        request = testing.DummyRequest()
        result = self._callFUT(
            request=request,
            easy_id=easy_id,
            auth_point=auth_point,
            req_time=req_time,
            org=org
        )
        print(result)
        result_tree = ElementTree.fromstring(result)

        # 正常終了していることを確認
        result_code = result_tree.find('data').find('result_code').text
        self.assertEqual(result_code, '0')
        # auth_pointで指定したポイントを確保できていることを確認
        secure_point = result_tree.find('data').find('secure_point').text
        self.assertEqual(secure_point, auth_point)

    @staticmethod
    def create_auth_stdonly_response():
        point_xml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" \
                    "<Root>" \
                    "<data>" \
                    "<easy_id>8235101</easy_id>" \
                    "<unique_id>52467328</unique_id>" \
                    "<secure_point>100</secure_point>" \
                    "<user_point>8900</user_point>" \
                    "<fix_point>8900</fix_point>" \
                    "<sec_able_point>8900</sec_able_point>" \
                    "<month_used_point>1100</month_used_point>" \
                    "<month_point>100000</month_point>" \
                    "<min_point>50</min_point>" \
                    "<order_max_point>30000</order_max_point>" \
                    "<res_time>2018-10-22 17:57:34</res_time>" \
                    "<result_code>0</result_code>" \
                    "</data>" \
                    "<confirmation_key>5eabcf7742c40b8e63b014142ea5a670</confirmation_key>" \
                    "</Root>"
        dom = parseString(point_xml)
        return dom.toprettyxml()


class FixTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.registry.settings = {
            'altair.point.endpoint': 'http://stg-point-api.stg.jp.local/',
            'altair.point.timeout': 20,
            'altair.point.secret_key': 'PANDA',
            'altair.point.RT.group_id': '468',
            'altair.point.RT.reason_id': '1904'
        }
        self.config.include('altair.point')

    def _callFUT(self, *args, **kwargs):
        from . import api
        # 実際に通信をする場合は以下の2行をコメントアウトしてください
        result_xml = mock.MagicMock(return_value=self.create_fix_response())
        api.fix = result_xml
        return api.fix(*args, **kwargs)

    def test_it(self):
        # authを実行したポイント充当のFix処理を行う
        easy_id = '8235101'
        fix_point = '100'
        unique_id = '52469475'  # 実際に通信する場合はauth-stdonlyで確保した際のunique_idに書き換えてください
        fix_id = 'FixTest_ticket01'
        group_id = '468'
        reason_id = '1904'
        req_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        request = testing.DummyRequest()
        result = self._callFUT(
            request=request,
            easy_id=easy_id,
            fix_point=fix_point,
            unique_id=unique_id,
            fix_id=fix_id,
            group_id=group_id,
            reason_id=reason_id,
            req_time=req_time,
        )
        print(result)
        result_tree = ElementTree.fromstring(result)

        # 正常終了していることを確認
        result_code = result_tree.find('data').find('result_code').text
        self.assertEqual(result_code, '0')
        # fix_pointで指定したポイントを確定できているか
        point_fix_point = result_tree.find('data').find('fix_point').text
        self.assertEqual(point_fix_point, fix_point)

    @staticmethod
    def create_fix_response():
        point_xml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" \
                    "<Root>" \
                    "<data>" \
                    "<easy_id>8235101</easy_id>" \
                    "<unique_id>52469475</unique_id>" \
                    "<fix_point>100</fix_point>" \
                    "<res_time>2018-10-22 16:19:19</res_time>" \
                    "<result_code>0</result_code>" \
                    "</data>" \
                    "<confirmation_key>5hrscf7742c40b8e63b078912ea5a670</confirmation_key>" \
                    "</Root>"
        dom = parseString(point_xml)
        return dom.toprettyxml()


class CancelTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.registry.settings = {
            'altair.point.endpoint': 'http://stg-point-api.stg.jp.local/',
            'altair.point.timeout': 20,
            'altair.point.secret_key': 'PANDA',
            'altair.point.RT.group_id': '468',
            'altair.point.RT.reason_id': '1904'
        }
        self.config.include('altair.point')

    def _callFUT(self, *args, **kwargs):
        from . import api
        # 実際に通信をする場合は以下の2行をコメントアウトしてください
        result_xml = mock.MagicMock(return_value=self.create_cancel_response())
        api.cancel = result_xml
        return api.cancel(*args, **kwargs)

    def test_it(self):
        # authを実行したポイント充当のFix処理を行う
        easy_id = '8235101'
        unique_id = '52469456'  # 実際に通信する場合はキャンセルをしたいunique_idに書き換えてください
        fix_id = 'FixTest_ticket01'
        group_id = '468'
        reason_id = '1904'
        req_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        request = testing.DummyRequest()
        result = self._callFUT(
            request=request,
            easy_id=easy_id,
            unique_id=unique_id,
            fix_id=fix_id,
            group_id=group_id,
            reason_id=reason_id,
            req_time=req_time,
        )
        print(result)
        result_tree = ElementTree.fromstring(result)

        # 正常終了していることを確認
        result_code = result_tree.find('data').find('result_code').text
        self.assertEqual(result_code, '0')
        # キャンセルが正常に処理され、ポイントから返却されたfix_pointが 0 になっていることを確認
        point_fix_point = result_tree.find('data').find('fix_point').text
        self.assertEqual(point_fix_point, '0')

    @staticmethod
    def create_cancel_response():
        point_xml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" \
                    "<Root>" \
                    "<data>" \
                    "<easy_id>8235101</easy_id>" \
                    "<unique_id>52469456</unique_id>" \
                    "<fix_point>0</fix_point>" \
                    "<res_time>2018-10-22 11:20:13</res_time>" \
                    "<result_code>0</result_code>" \
                    "</data>" \
                    "<confirmation_key>655d1656712cd74ef334f89ff7541a82</confirmation_key>" \
                    "</Root>"
        dom = parseString(point_xml)
        return dom.toprettyxml()


class RollbackTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.registry.settings = {
            'altair.point.endpoint': 'http://stg-point-api.stg.jp.local/',
            'altair.point.timeout': 20,
            'altair.point.secret_key': 'PANDA',
            'altair.point.RT.group_id': '468',
            'altair.point.RT.reason_id': '1904'
        }
        self.config.include('altair.point')

    def _callFUT(self, *args, **kwargs):
        from . import api
        # 実際に通信をする場合は以下の2行をコメントアウトしてください
        result_xml = mock.MagicMock(return_value=self.create_rollback_response())
        api.rollback = result_xml
        return api.rollback(*args, **kwargs)

    def test_it(self):
        # rollbackを実行したポイント充当のFix処理を行う
        easy_id = '8235101'
        unique_id = '52469475'
        group_id = '468'
        reason_id = '1904'

        request = testing.DummyRequest()
        result = self._callFUT(
            request=request,
            easy_id=easy_id,
            unique_id=unique_id,
            group_id=group_id,
            reason_id=reason_id,
        )
        print(result)
        result_tree = ElementTree.fromstring(result)

        # 正常終了していることを確認
        result_code = result_tree.find('data').find('result_code').text
        self.assertEqual(result_code, '0')

    @staticmethod
    def create_rollback_response():
        point_xml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" \
                    "<Root>" \
                    "<data>" \
                    "<easy_id>8235101</easy_id>" \
                    "<unique_id>52469475</unique_id>" \
                    "<res_time>2018-10-22 16:30:06</res_time>" \
                    "<result_code>0</result_code>" \
                    "</data>" \
                    "<confirmation_key>774a81269a95ad5bd127088008b507b3</confirmation_key>" \
                    "</Root>"
        dom = parseString(point_xml)
        return dom.toprettyxml()
