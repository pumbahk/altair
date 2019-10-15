# -*- coding: utf-8 -*-

import mock
import unittest
from pyramid.testing import DummyResource, DummyModel
from altair.app.ticketing.testing import DummyRequest


class SkidataPropertyViewTest(unittest.TestCase):
    @staticmethod
    def _make_test_target(*args, **kwargs):
        from altair.app.ticketing.skidata.views import SkidataPropertyView
        return SkidataPropertyView(*args, **kwargs)

    @mock.patch('altair.app.ticketing.skidata.models.SkidataProperty.find_all_by_org_id')
    @mock.patch('altair.app.ticketing.skidata.views.get_db_session')
    def test_show(self, get_db_session, find_all_by_org_id):
        """ 正常系テスト """
        from altair.app.ticketing.skidata.models import SkidataPropertyTypeEnum
        prop_for_sales_segment_group = DummyModel(prop_type=SkidataPropertyTypeEnum.SalesSegmentGroup.v)
        prop_for_product_item = DummyModel(prop_type=SkidataPropertyTypeEnum.ProductItem.v)
        get_db_session.return_value = DummyModel()
        find_all_by_org_id.return_value = [prop_for_sales_segment_group, prop_for_product_item]
        test_context = DummyResource(user=DummyModel(organization=DummyModel(id=1)))
        test_view = self._make_test_target(test_context, DummyRequest())

        result_dict = test_view.show()
        self.assertEqual(len(result_dict['props_for_sales_segment_group']), 1)
        self.assertEqual(result_dict['props_for_sales_segment_group'][0], prop_for_sales_segment_group)
        self.assertEqual(len(result_dict['props_for_product_item']), 1)
        self.assertEqual(result_dict['props_for_product_item'][0], prop_for_product_item)

    def test_show_new_prop_form_for_sales_segment_group(self):
        """ 正常系テスト 販売区分グループ向け処理 """
        from altair.app.ticketing.skidata.models import SkidataPropertyTypeEnum
        test_prop_type = SkidataPropertyTypeEnum.SalesSegmentGroup
        test_request = DummyRequest(matchdict=dict(prop_type=test_prop_type.k))
        test_view = self._make_test_target(DummyResource(), test_request)

        result_dict = test_view.show_new_prop_form()
        self.assertEqual(result_dict['prop_type'], test_prop_type)
        self.assertIsNotNone(result_dict['form'])

    def test_show_new_prop_form_for_product_item(self):
        """ 正常系テスト 商品明細向け処理 """
        from altair.app.ticketing.skidata.models import SkidataPropertyTypeEnum
        test_prop_type = SkidataPropertyTypeEnum.ProductItem
        test_request = DummyRequest(matchdict=dict(prop_type=test_prop_type.k))
        test_view = self._make_test_target(DummyResource(), test_request)

        result_dict = test_view.show_new_prop_form()
        self.assertEqual(result_dict['prop_type'], test_prop_type)
        self.assertIsNotNone(result_dict['form'])

    def test_show_new_prop_form_invalid_type(self):
        """ 異常系テスト 無効なタイプを指定 """
        from pyramid.httpexceptions import HTTPFound

        def mock_route_path(route_name):
            return u'http://example.com'

        test_request = DummyRequest(matchdict=dict(prop_type=u'unsupported_type'), route_path=mock_route_path)
        test_view = self._make_test_target(DummyResource(), test_request)
        return_value = test_view.show_new_prop_form()
        self.assertIsInstance(return_value, HTTPFound)

    @mock.patch('altair.app.ticketing.skidata.models.SkidataProperty.insert_new_property')
    def test_create_property_success(self, insert_new_property):
        """ 正常系テスト プロパティ登録成功 """
        from altair.app.ticketing.skidata.models import SkidataPropertyTypeEnum
        from pyramid.httpexceptions import HTTPFound

        def mock_route_path(route_name):
            return u'http://example.com'

        flash_list = list()

        def flash(msg):
            flash_list.append(msg)

        test_params = dict(name=u'test_name', value=u'1')
        test_context = DummyResource(user=DummyModel(organization=DummyModel(id=1)))
        test_request = DummyRequest(
            matchdict=dict(prop_type=SkidataPropertyTypeEnum.SalesSegmentGroup.k),
            POST=test_params,
            route_path=mock_route_path,
            session=DummyModel(flash=flash)
        )
        new_prop = DummyModel(id=1)
        insert_new_property.return_value = new_prop
        test_view = self._make_test_target(test_context, test_request)
        return_value = test_view.create_property()

        self.assertIsInstance(return_value, HTTPFound)
        self.assertEqual(flash_list[0], u'登録完了しました[id={}]'.format(new_prop.id))

    def test_create_property_invalid_type(self):
        """ 異常系テスト 無効なタイプを指定 """
        from pyramid.httpexceptions import HTTPFound

        def mock_route_path(route_name):
            return u'http://example.com'

        flash_list = list()

        def flash(msg):
            flash_list.append(msg)

        test_params = dict(name=u'test_name', value=u'1')
        test_context = DummyResource(user=DummyModel(organization=DummyModel(id=1)))
        test_request = DummyRequest(
            matchdict=dict(prop_type=u'unsupported_type'),
            POST=test_params,
            route_path=mock_route_path,
            session=DummyModel(flash=flash)
        )
        test_view = self._make_test_target(test_context, test_request)
        return_value = test_view.create_property()

        self.assertIsInstance(return_value, HTTPFound)
        self.assertEqual(flash_list[0], u'不正なページ遷移です。')

    def test_create_property_invalid_form(self):
        """ 異常系テスト 無効な入力内容 """
        from altair.app.ticketing.skidata.models import SkidataPropertyTypeEnum

        def mock_route_path(route_name):
            return u'http://example.com'

        flash_list = list()

        def flash(msg):
            flash_list.append(msg)

        test_params = dict(name=u'test_name', value=u'test_value')
        test_context = DummyResource(user=DummyModel(organization=DummyModel(id=1)))
        test_request = DummyRequest(
            matchdict=dict(prop_type=SkidataPropertyTypeEnum.SalesSegmentGroup.k),
            POST=test_params,
            route_path=mock_route_path,
            session=DummyModel(flash=flash)
        )
        test_view = self._make_test_target(test_context, test_request)
        return_value = test_view.create_property()

        self.assertEqual(flash_list[0], u'入力内容に誤りがあります。')

    @mock.patch('altair.app.ticketing.skidata.models.SkidataProperty.find_by_id')
    @mock.patch('altair.app.ticketing.skidata.views.get_db_session')
    def test_show_edit_prop_form(self, get_db_session, find_by_id):
        """ 正常系テスト """

        def mock_route_path(route_name):
            return u'http://example.com'

        test_request = DummyRequest(
            matchdict=dict(id=1),
            route_path=mock_route_path
        )
        test_property = DummyModel(id=1, name=u'テスト', value=10)
        find_by_id.return_value = test_property
        test_view = self._make_test_target(DummyResource(), test_request)
        return_dict = test_view.show_edit_prop_form()

        self.assertEqual(return_dict['prop_id'], test_property.id)
        self.assertIsNotNone(return_dict['form'])

    @mock.patch('altair.app.ticketing.skidata.models.SkidataProperty.find_by_id')
    @mock.patch('altair.app.ticketing.skidata.views.get_db_session')
    def test_show_edit_prop_no_data(self, get_db_session, find_by_id):
        """ 異常系テスト 指定したSkidataPropertyが存在しない """
        from sqlalchemy.orm.exc import NoResultFound
        from pyramid.httpexceptions import HTTPFound

        def mock_route_path(route_name):
            return u'http://example.com'

        test_request = DummyRequest(
            matchdict=dict(id=1),
            route_path=mock_route_path
        )
        find_by_id.side_effect = NoResultFound
        test_view = self._make_test_target(DummyResource(), test_request)
        return_value = test_view.show_edit_prop_form()

        self.assertIsInstance(return_value, HTTPFound)

    @mock.patch('altair.app.ticketing.skidata.models.SkidataProperty.update_property')
    def test_update_property(self, update_property):
        """ 正常系テスト """
        from pyramid.httpexceptions import HTTPFound

        def mock_route_path(route_name):
            return u'http://example.com'

        flash_list = list()

        def flash(msg):
            flash_list.append(msg)

        test_params = dict(name=u'test_name', value=u'1')
        test_request = DummyRequest(
            matchdict=dict(id=1),
            POST=test_params,
            route_path=mock_route_path,
            session=DummyModel(flash=flash)
        )
        prop_updated = DummyModel(id=1)
        update_property.return_value = prop_updated
        test_view = self._make_test_target(DummyResource(), test_request)
        return_value = test_view.update_property()

        self.assertIsInstance(return_value, HTTPFound)
        self.assertEqual(flash_list[0], u'更新しました[id={}]'.format(prop_updated.id))

    @mock.patch('altair.app.ticketing.skidata.models.SkidataProperty.update_property')
    def test_update_property_no_data(self, update_property):
        """ 異常系テスト プロパティが存在しない """
        from sqlalchemy.orm.exc import NoResultFound
        from pyramid.httpexceptions import HTTPFound

        def mock_route_path(route_name):
            return u'http://example.com'

        flash_list = list()

        def flash(msg):
            flash_list.append(msg)

        test_params = dict(name=u'test_name', value=u'1')
        test_request = DummyRequest(
            matchdict=dict(id=1),
            POST=test_params,
            route_path=mock_route_path,
            session=DummyModel(flash=flash)
        )
        update_property.side_effect = NoResultFound
        test_view = self._make_test_target(DummyResource(), test_request)
        return_value = test_view.update_property()

        self.assertIsInstance(return_value, HTTPFound)
        self.assertEqual(flash_list[0], u'対象のデータが存在しません')

    def test_update_property_invalid_form(self):
        """ 異常系テスト フォーム入力内容が不正 """
        def mock_route_path(route_name):
            return u'http://example.com'

        flash_list = list()

        def flash(msg):
            flash_list.append(msg)

        test_params = dict(name=u'test_name', value=u'test_value')
        test_request = DummyRequest(
            matchdict=dict(id=1),
            POST=test_params,
            route_path=mock_route_path,
            session=DummyModel(flash=flash)
        )

        test_view = self._make_test_target(DummyResource(), test_request)
        test_view.update_property()

        self.assertEqual(flash_list[0], u'入力内容に誤りがあります。')

    @mock.patch('altair.app.ticketing.skidata.models.SkidataProperty.delete_property')
    def test_delete_property(self, delete_property):
        """ 正常系テスト """
        from pyramid.httpexceptions import HTTPFound
        def mock_route_path(route_name):
            return u'http://example.com'

        flash_list = list()

        def flash(msg):
            flash_list.append(msg)

        test_prop_id = 1
        test_params = dict(name=u'test_name', value=u'1')
        test_request = DummyRequest(
            matchdict=dict(id=test_prop_id),
            POST=test_params,
            route_path=mock_route_path,
            session=DummyModel(flash=flash)
        )
        test_view = self._make_test_target(DummyResource(), test_request)
        return_value = test_view.delete_property()

        self.assertIsInstance(return_value, HTTPFound)
        self.assertEqual(flash_list[0], u'対象のプロパティを削除しました[id={}]'.format(test_prop_id))

    @mock.patch('altair.app.ticketing.skidata.models.SkidataProperty.delete_property')
    def test_delete_property_nodata(self, delete_property):
        """ 異常系テスト データなし """
        from sqlalchemy.orm.exc import NoResultFound
        from pyramid.httpexceptions import HTTPFound
        def mock_route_path(route_name):
            return u'http://example.com'

        flash_list = list()

        def flash(msg):
            flash_list.append(msg)

        test_prop_id = 1
        test_params = dict(name=u'test_name', value=u'1')
        test_request = DummyRequest(
            matchdict=dict(id=test_prop_id),
            POST=test_params,
            route_path=mock_route_path,
            session=DummyModel(flash=flash)
        )
        delete_property.side_effect = NoResultFound
        test_view = self._make_test_target(DummyResource(), test_request)
        return_value = test_view.delete_property()

        self.assertIsInstance(return_value, HTTPFound)
        self.assertEqual(flash_list[0], u'対象のデータが存在しません')
