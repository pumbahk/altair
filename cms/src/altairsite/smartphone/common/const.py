# -*- coding: utf-8 -*-
class Region(object):
    def __init__(self, name, areas):
        self.name = name
        self.areas = areas

def getRegions():
    regions = []
    regions.append(Region('hokkaido', ['hokkaido','aomori','iwate','akita','miyagi','yamagata','fukushima']))
    regions.append(Region('syutoken', ['chiba','tokyo','kanagawa','ibaraki','tochigi','gunma','saitama','yamanashi']))
    regions.append(Region('koshinetsu', ['nagano','niigata','gifu','aichi','mie','shizuoka']))
    regions.append(Region('kinki', ['kyoto','osaka','hyogo','shiga','nara','wakayama','toyama','ishikawa','fukui']))
    regions.append(Region('chugoku', ['hiroshima','okayama','tottori','shimane','yamaguchi','tokushima','kagawa','ehime','kouchi']))
    regions.append(Region('kyusyu', ['okinawa', 'fukuoka','saga','nagasaki','kumamoto','oita','miyazaki','kagoshima']))
    return regions
