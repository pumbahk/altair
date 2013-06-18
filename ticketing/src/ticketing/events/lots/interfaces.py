# -*- coding:utf-8 -*-
from zope.interface import Interface, Attribute

"""
件数ベース

申込件数	当選件数	決済件数	予約件数	キャンセル・流れ
250	150	135	10	 5

枚数ベース
　　	　　　　　	希望順位別内訳枚数
　　	申込総枚数	第一希望	第二希望	第三希望	...
総数	 500	 350	 85	63	...

公演日時	席種	申込数枚数	　希望順位内訳枚数	当選数	決済済	予約数	キャンセル・流れ
第一希望	第二希望	第三希望	..
2013/6/1（土）17:00	SS席	 35	20	10	5	･･･	20	18	2	0
2013/6/1（土）17:00	S席	100	80	5	15	･･･	75	70	4	1
2013/6/1（土）17:00	A席	 50	45	5	3	･･･	55	55	0	0
2013/6/2（日）15:00	SS席	85	55	25	0	･･･	20	15	3	2
2013/6/2（日）15:00	S席	150	100	20	30	･･･	75	63	7	5
2013/6/2（日）15:00	A席	80	50	20	10	･･･	55	50	3	2
総数	500	350	85	63	･･･	300	271	19	10

    """


class ILotEntryStatus(Interface):
    """ """
    performances = Attribute(u"公演")
    wishes = Attribute(u"希望順位別内訳枚数")

    total_entries = Attribute(u"申込件数")
    elected_count = Attribute(u"当選件数")
    ordered_count = Attribute(u"決済件数")
    reserved_count = Attribute(u"予約件数")
    canceled_count = Attribute(u"キャンセル・流れ")

    total_quantity = Attribute(u"申込総枚数")

class ILotEntryWishStatus(Interface):
    """ 希望順位別内訳枚数"""

    wish_order = Attribute(u"希望順位")
    quantity = Attribute(u"申込枚数")

class ILotEntryPerformanceSeatTypeStatus(Interface):
    """ 公演席種ごとの抽選申し込み状況"""
    performance = Attribute(u"公演")
    seat_type = Attribute(u"席種")
    entry_quantity = Attribute(u"申込総枚数")
    elected_quantity = Attribute(u"当選件数")
    ordered_quantity = Attribute(u"決済件数")
    reserved_quantity = Attribute(u"予約件数")

class ILotEntryPerformanceSeatTypesWishStatus(Interface):
    """ """
    Attribute(u"希望順位")
    Attribute(u"申込枚数")
