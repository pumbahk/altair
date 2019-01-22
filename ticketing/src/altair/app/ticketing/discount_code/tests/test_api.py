# -*- coding:utf-8 -*-

import unittest

from altair.app.ticketing.cart.models import CartedProductItem
from altair.app.ticketing.cart.schemas import DiscountCodeForm
from altair.app.ticketing.core.models import ProductItem
from altair.app.ticketing.discount_code import api
from altair.app.ticketing.discount_code.models import DiscountCodeSetting


class CalcAppliedAmountTests(unittest.TestCase):
    """
    管理画面の割引設定が正しく割引適用金額の計算に反映されているかをテストする
    """

    def setUp(self):

        # 割引適用金額の元となるdictの初期化
        self.code_dict = {
            'code': u'TFA86CYCKRYT',
            'form': DiscountCodeForm(),
            'carted_product_item': CartedProductItem(
                product_item=ProductItem()
            ),
            'discount_code_setting': DiscountCodeSetting()
        }

    def tearDown(self):
        pass

    def test_100_per_discount(self):
        """
        割引率100%
        商品明細単価自体と同じ適用金額となる
        :return: True
        """
        self.code_dict['carted_product_item'].product_item.price = 12345
        self.code_dict['discount_code_setting'].benefit_amount = 100
        self.code_dict['discount_code_setting'].benefit_unit = u'%'

        self.assertEqual(api.calc_applied_amount(self.code_dict), 12345)

    def test_33_per_discount(self):
        """
        割引率33%
        割り切れない適用金額となる割引設定は小数点以下を切り捨て
        :return: True
        """
        self.code_dict['carted_product_item'].product_item.price = 12345
        self.code_dict['discount_code_setting'].benefit_amount = 33
        self.code_dict['discount_code_setting'].benefit_unit = u'%'

        self.assertEqual(api.calc_applied_amount(self.code_dict), 4073)

    def test_0_per_discount(self):
        """
        割引率0%
        無意味な割引設定だが、設定可能なためテスト
        :return: True
        """
        self.code_dict['carted_product_item'].product_item.price = 12345
        self.code_dict['discount_code_setting'].benefit_amount = 0
        self.code_dict['discount_code_setting'].benefit_unit = u'%'

        self.assertEqual(api.calc_applied_amount(self.code_dict), 0)

    def test_2000_yen_discount(self):
        """
        2000円引き
        実運用でよくありそうな割引設定
        :return: True
        """
        self.code_dict['carted_product_item'].product_item.price = 12345
        self.code_dict['discount_code_setting'].benefit_amount = 2000
        self.code_dict['discount_code_setting'].benefit_unit = u'y'

        self.assertEqual(api.calc_applied_amount(self.code_dict), 2000)

    def test_over_amount_yen_discount(self):
        """
        商品明細単価を上回る値引き
        現金をプレゼントする訳にはいかないので、商品明細単価が割引の上限となる
        なお、テストで設定しているbenefit_amountは最大の設定数値
        :return: True
        """
        self.code_dict['carted_product_item'].product_item.price = 12345
        self.code_dict['discount_code_setting'].benefit_amount = 99999999999
        self.code_dict['discount_code_setting'].benefit_unit = u'y'

        self.assertEqual(api.calc_applied_amount(self.code_dict), 12345)

    def test_what_if_when_price_is_free(self):
        """
        ありえない運用だが、商品明細単価が無料のものがあったとして、そこに割引コードが適用されたら？
        :return: True
        """
        self.code_dict['carted_product_item'].product_item.price = 0
        self.code_dict['discount_code_setting'].benefit_amount = 33
        self.code_dict['discount_code_setting'].benefit_unit = u'%'

        self.assertEqual(api.calc_applied_amount(self.code_dict), 0)
