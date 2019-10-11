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
        from pyramid.httpexceptions import HTTPFound

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
