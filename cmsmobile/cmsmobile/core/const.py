# -*- coding: utf-8 -*-
from standardenum import StandardEnum

class SalesEnum(StandardEnum):
    ON_SALE         = 0
    WEEK_SALE       = 1
    NEAR_SALE_END   = 2

def get_prefecture_name(area):
    areas = {
         '1':u'首都圏'
        ,'2':u'近畿'
        ,'3':u'東海'
        ,'4':u'北海道'
        ,'5':u'東北'
        ,'6':u'北関東'
        ,'7':u'甲信越'
        ,'8':u'北陸'
        ,'9':u'中国'
        ,'10':u'四国'
        ,'11':u'九州'
        ,'12':u'沖縄'
    }
    return areas[area]

def get_prefecture(area):
    areas = {
        '1':['chiba','tokyo','kanagawa']
        ,'2':['shiga','kyoto','osaka','hyogo','nara','wakayama']
        ,'3':['gifu','aichi','mie','shizuoka']
        ,'4':['hokkaido']
        ,'5':['aomori', 'iwate', 'akita', 'miyagi', 'yamagata', 'fukushima']
        ,'6':['ibaraki','tochigi','gunma','saitama']
        ,'7':['niigata','yamanashi','nagano']
        ,'8':['toyama','ishikawa','fukui']
        ,'9':['tottori','shimane','okayama','hiroshima','yamaguchi']
        ,'10':['tokushima','kagawa','ehime','kouchi']
        ,'11':['fukuoka','saga','nagasaki','kumamoto','oita','miyazaki','kagoshima']
        ,'12':['okinawa']
    }
    return areas[str(area)]
