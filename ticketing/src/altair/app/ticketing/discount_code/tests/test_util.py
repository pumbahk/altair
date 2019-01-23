# -*- coding:utf-8 -*-

"""
parameterizedを利用して複数パターンを少ないメソッドでテストしています。
参考: https://qiita.com/nittyan/items/0152a3b93e17c177f5f5

追記：parameterized 0.6.1 をticketing/setup.pyで依存関係作成するとバッチサーバでのバッチ起動時に
     pkg_resources.DistributionNotFound: parameterized==0.6.1
     のエラーが出てしまい処理ができない事象を検知したのでこのテストコードはコメントアウトしています。
     テストをする際はparameterizedを一時的にインポートする、または根本原因を解決して利用するようにしてください。
"""

"""
import unittest
from datetime import datetime

from altair.app.ticketing.cart.models import CartedProductItem
from altair.app.ticketing.core.models import ProductItem
from altair.app.ticketing.discount_code import util
from altair.app.ticketing.discount_code.models import DiscountCodeSetting, DiscountCodeTarget, \
    DiscountCodeTargetStockType
from altair.app.ticketing.testing import _setup_db, _teardown_db
from parameterized import parameterized
from pyramid.path import DottedNameResolver

# モデル間の依存性解消
dependency_modules = [
    'altair.app.ticketing.orders.models',
    'altair.app.ticketing.cart.models',
    'altair.app.ticketing.core.models',
]
resolver = DottedNameResolver()
for dm in dependency_modules:
    resolver.resolve(dm)


class FindAvailableDcSettingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.session = _setup_db(modules=dependency_modules)

        # テスト用のデータ登録
        # テスト中にデータの更新がないので、setUpで都度初期化せずに一度だけデータ作成しています
        test_setting_list = [
            DiscountCodeSetting(
                id=1,
                first_digit=u'T',
                following_2to4_digits=u'123',
                name=u'自社発行3000円引き割引コード',
                issued_by=u'own',
                criterion=u'price',
                condition_price_amount=5000,
                condition_price_more_or_less=u'less',
                benefit_amount=3000,
                benefit_unit=u'y',
                organization_id=1,
                is_valid=1,
                start_at=datetime(2017, 4, 15, 9, 0, 0),
                end_at=datetime(2018, 12, 27, 18, 0, 0),
                explanation=u'<p><strong>自社発行 指定の席種と公演は3000円引き！</strong></p>',
                dc_targets=[DiscountCodeTarget(
                    id=1,
                    discount_code_setting_id=1,
                    event_id=1,
                    performance_id=1
                )],
                dc_target_stock_types=[DiscountCodeTargetStockType(
                    id=1,
                    discount_code_setting_id=1,
                    event_id=1,
                    performance_id=1,
                    stock_type_id=1,
                )]
            ),
            DiscountCodeSetting(
                id=2,
                first_digit=u'E',
                following_2to4_digits=u'456',
                name=u'スポーツサービス発行30%引き割引コード',
                issued_by=u'sports_service',
                criterion=u'price',
                condition_price_amount=3000,
                condition_price_more_or_less=u'less',
                benefit_amount=30,
                benefit_unit=u'%',
                organization_id=1,
                is_valid=1,
                start_at=datetime(2017, 4, 15, 9, 0, 0),
                end_at=datetime(2018, 12, 27, 18, 0, 0),
                explanation=u'<p><strong>スポーツサービス発行30%引き割引コード 指定の公演で3,000円以下の商品は30%引き！</strong></p>',
                dc_targets=[DiscountCodeTarget(
                    id=2,
                    discount_code_setting_id=2,
                    event_id=1,
                    performance_id=2
                )],
                dc_target_stock_types=[]
            ),
            DiscountCodeSetting(
                id=3,
                first_digit=u'E',
                following_2to4_digits=u'789',
                name=u'スポーツサービス発行100%引き割引コード',
                issued_by=u'sports_service',
                criterion=u'price',
                condition_price_amount=10000,
                condition_price_more_or_less=u'less',
                benefit_amount=100,
                benefit_unit=u'%',
                organization_id=1,
                is_valid=1,
                start_at=datetime(2017, 4, 15, 9, 0, 0),
                end_at=datetime(2018, 12, 27, 18, 0, 0),
                explanation=u'<p><strong>スポーツサービス発行100%引き割引コード 指定の公演で10,000円以下の商品は100%引き！</strong></p>',
                dc_targets=[DiscountCodeTarget(
                    id=3,
                    discount_code_setting_id=3,
                    event_id=1,
                    performance_id=2
                )],
                dc_target_stock_types=[]
            ),
            DiscountCodeSetting(
                id=4,
                first_digit=u'T',
                following_2to4_digits=u'456',
                name=u'自社発行1000円引き割引コード',
                issued_by=u'own',
                criterion=u'price',
                condition_price_amount=1,
                condition_price_more_or_less=u'less',
                benefit_amount=1000,
                benefit_unit=u'y',
                organization_id=1,
                is_valid=1,
                start_at=datetime(2017, 4, 15, 9, 0, 0),
                end_at=datetime(2018, 12, 27, 18, 0, 0),
                explanation=u'<p><strong>自社発行 指定の席種1000円引き！</strong></p>',
                dc_targets=[],
                dc_target_stock_types=[DiscountCodeTargetStockType(
                    id=2,
                    discount_code_setting_id=4,
                    event_id=1,
                    performance_id=1,
                    stock_type_id=1,
                )]
            ),
        ]

        cls.session.add_all(test_setting_list)
        cls.session.flush()

    @classmethod
    def tearDownClass(cls):
        _teardown_db()

    @staticmethod
    def _make_condition(args):
        # find_available_target_settingsに渡す条件をdictで作成
        keys = [
            'performance_id',
            'stock_type_ids',
            'issued_by',
            'first_4_digits',
            'max_price',
            'session',
            'refer_all',
            'now'
        ]

        res = {}
        for key, arg in zip(keys, args):
            res.update({key: arg})

        return res

    @parameterized.expand([
        (1, [1], u'own', u'T123', 4999, None, False, datetime(2018, 12, 23, 18, 0, 0)),  # 適用公演・適用席種で該当
        (1, [1], u'own', u'T123', 5001, None, False, datetime(2018, 12, 23, 18, 0, 0)),  # 適用公演で該当
        (1, [2], u'own', u'T123', 4999, None, False, datetime(2018, 12, 23, 18, 0, 0)),  # 適用席種で該当
    ])
    def test_found_properly_one(self, *args):
        # 割引コード設定が一つだけ見つかる
        cond = self._make_condition(args)
        found = util.find_available_target_settings(**cond)
        self.assertNotEqual([], found)
        self.assertEqual(1, found.id)
        self.assertEqual(u'自社発行3000円引き割引コード', found.name)

    @parameterized.expand([
        (2, [1], u'sports_service', None, 100, None, False, datetime(2018, 12, 23, 18, 0, 0)),  # 適用公演で該当
        (1, [1], None, None, 4999, None, False, datetime(2018, 12, 23, 18, 0, 0)),  # 自社発行3000円引き割引コードが適用公演で、自社発行1000円引き割引コードが適用席種で該当
    ])
    def test_found_properly_multiple(self, *args):
        # 割引コード設定が複数見つかる
        cond = self._make_condition(args)
        found = util.find_available_target_settings(**cond)
        self.assertGreaterEqual(2, len(found))

    @parameterized.expand([
        (1, [2], u'own', u'T123', 5001, None, False, datetime(2018, 12, 23, 18, 0, 0)),  # 適用公演・適用席種に当てはまらない
        (1, [1], u'own', u'T123', 4999, None, False, datetime(2018, 12, 27, 18, 0, 1)),  # 適用終了日時オーバー
    ])
    def test_do_not_found(self, *args):
        # 割引コード設定が見つかってはいけない
        cond = self._make_condition(args)
        found = util.find_available_target_settings(**cond)
        self.assertEqual([], found)


class CalcAppliedAmountTests(unittest.TestCase):
"""
# 管理画面の割引設定が正しく割引適用金額の計算に反映されているかをテスト
"""

    def setUp(self):
        # 割引適用金額の元となる要素の初期化
        self.carted_product_item = CartedProductItem(product_item=ProductItem())
        self.setting = DiscountCodeSetting()

    def tearDown(self):
        pass

    @parameterized.expand([
        (12345, 100, u'%', 12345),  # 割引率100%。 商品明細単価自体と同じ適用金額となる
        (12345, 33, u'%', 4073),  # 割引率33%。割り切れない適用金額となる割引設定は小数点以下を切り捨て
        (12345, 0, u'%', 0),  # 割引率0%。無意味な割引設定だが、設定可能なためテスト
        (12345, 2000, u'y', 2000),  # 2000円引き。実運用でよくありそうな割引設定
        (12345, 99999999999, u'y', 12345),  # 商品明細単価を上回る値引き。benefit_amountは最大の設定数値
        (0, 33, u'%', 0),  # 商品明細単価が無料のものがあったとして、そこに割引コードが適用されたら？
    ])
    def test_multiple_patterns(self, item_price, benefit_amount, benefit_unit, expected):
        # parameterizedを利用して複数パターンをテスト
        self.carted_product_item.product_item.price = item_price
        self.setting.benefit_amount = benefit_amount
        self.setting.benefit_unit = benefit_unit

        self.assertEqual(util.calc_applied_amount(
            self.setting,
            self.carted_product_item
        ), expected)
"""