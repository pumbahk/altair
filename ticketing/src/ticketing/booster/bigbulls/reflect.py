# -*- coding:utf-8 -*-

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
    "authenticated_uniform", 
    "for_kids")

ms = MemberTypeSymbols = SymbolPool(
    gold=u"ゴールド会員", 
    silver_with_authencated=u"シルバー会員+半額購入特典", 
    silver=u"シルバー会員", 
    red=u"レッド会員", 
    kids=u"キッズ会員"
    )

product_reflections = {
    ms.gold: [s.authenticated_uniform], 
    ms.silver_with_authencated: [s.authenticated_uniform], 
    ms.silver: [s.replica_uniform], 
    ms.red: [s.t_shirts_size], 
    ms.kids: [s.for_kids]
    ## 年齢がN歳以下をどうしようか
}

