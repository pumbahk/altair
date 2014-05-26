# -*- coding: utf-8 -*-
from standardenum import StandardEnum

class SalesEnum(StandardEnum):
    ON_SALE         = 0
    WEEK_SALE       = 1
    NEAR_SALE_END   = 2
    SOON_ACT        = 3
    GENRE           = 4
    ALL             = 5

class Area(object):
    def __init__(self, name, prefectures):
        self.name = name
        self.prefectures = prefectures

def get_areas():
    areas = []
    areas.append(Area('hokkaido', ['hokkaido','aomori','iwate','akita','miyagi','yamagata','fukushima']))
    areas.append(Area('syutoken', ['chiba','tokyo','kanagawa','ibaraki','tochigi','gunma','saitama','yamanashi']))
    areas.append(Area('koshinetsu', ['nagano','niigata','gifu','aichi','mie','shizuoka']))
    areas.append(Area('kinki', ['kyoto','osaka','hyogo','shiga','nara','wakayama','toyama','ishikawa','fukui']))
    areas.append(Area('chugoku', ['hiroshima','okayama','tottori','shimane','yamaguchi','tokushima','kagawa','ehime','kouchi']))
    areas.append(Area('kyusyu', ['okinawa', 'fukuoka','saga','nagasaki','kumamoto','oita','miyazaki','kagoshima']))
    return areas

def get_prefectures(target_area):
    areas = get_areas()
    for area in areas:
        if area.name == target_area:
            return area.prefectures

