# -*- coding:utf-8 -*-

"""
Product.nameでの分岐は脆い。他に手軽で良い方法が見つかっていない
"""
def identify_product(product):
    return product.name

def form_permissions_from_product(product, default=None):
    return product_reflections.get(identify_product(product), default) 

class SymbolPool(object):
    def __init__(self, *args, **kwargs):
        for k in args:
            setattr(self, k, k)
        for k, v in kwargs.items():
            setattr(self, k, v)

s = Symbols = SymbolPool(
    "publicity",
    "t_shirts_size",
    "official_ball",
    "coupon")

ms = MemberTypeSymbols = SymbolPool(
    platinum=u"プラチナプラン",
    gold=u"ゴールドプラン",
    regular=u"レギュラープラン",
    junior=u"ジュニアプラン"
    )

product_reflections = {
    ms.platinum: [s.publicity, s.t_shirts_size, s.coupon, s.official_ball],
    ms.gold: [s.publicity, s.t_shirts_size, s.coupon],
    ms.regular: [s.coupon],
    ms.junior: []
    ## 年齢がN歳以下をどうしようか
}

