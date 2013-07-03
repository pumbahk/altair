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
    "t_shirts_size", 
    "replica_uniform", 
    "authentic_uniform", 
    "for_kids")

ms = MemberTypeSymbols = SymbolPool(
    gold=u"ゴールド会員", 
    silver_with_authentic_uniform=u"シルバー会員（オーセンティックユニフォーム購入希望）", 
    silver=u"シルバー会員", 
    red=u"レッド会員", 
    kids=u"キッズ会員"
    )

product_reflections = {
    ms.gold: [s.authentic_uniform], 
    ms.silver_with_authentic_uniform: [s.authentic_uniform, s.replica_uniform], 
    ms.silver: [s.replica_uniform], 
    ms.red: [s.t_shirts_size], 
    ms.kids: [s.for_kids]
    ## 年齢がN歳以下をどうしようか
}

