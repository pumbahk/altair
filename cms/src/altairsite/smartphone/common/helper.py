# -*- coding: utf-8 -*-
import logging

logger = logging.getLogger(__file__)

class SmartPhoneHelper(object):
    def getRegionJapanese(self, keyword):
        regions = {
             'hokkaido':u'北海道・東北'
            ,'syutoken':u'首都圏・北関東'
            ,'koshinetsu':u'甲信越・東海'
            ,'kinki':u'近畿・北陸'
            ,'chugoku':u'中国・四国'
            ,'kyusyu':u'九州・沖縄'
        }
        return regions[keyword]

    def getAreaJapanese(self, keyword):
        areas = {
             'hokkaido':u'北海道'
            ,'aomori':u'青森'
            ,'iwate':u'岩手'
            ,'akita':u'秋田'
            ,'miyagi':u'宮城'
            ,'yamagata':u'山形'
            ,'fukushima':u'福島'
            ,'chiba':u'千葉'
            ,'tokyo':u'東京'
            ,'kanagawa':u'神奈川'
            ,'ibaraki':u'茨城'
            ,'tochigi':u'栃木'
            ,'gunma':u'群馬'
            ,'saitama':u'埼玉'
            ,'yamanashi':u'山梨'
            ,'nagano':u'長野'
            ,'niigata':u'新潟'
            ,'gifu':u'岐阜'
            ,'aichi':u'愛知'
            ,'mie':u'三重'
            ,'shizuoka':u'静岡'
            ,'kyoto':u'京都'
            ,'osaka':u'大阪'
            ,'hyogo':u'兵庫'
            ,'shiga':u'滋賀'
            ,'nara':u'奈良'
            ,'wakayama':u'和歌山'
            ,'toyama':u'富山'
            ,'ishikawa':u'石川'
            ,'fukui':u'福井'
            ,'hiroshima':u'広島'
            ,'okayama':u'岡山'
            ,'tottori':u'鳥取'
            ,'shimane':u'島根'
            ,'yamaguchi':u'山口'
            ,'tokushima':u'徳島'
            ,'kagawa':u'香川'
            ,'ehime':u'愛媛'
            ,'kouchi':u'高知'
            ,'okinawa':u'沖縄'
            ,'fukuoka':u'福岡'
            ,'saga':u'佐賀'
            ,'nagasaki':u'長崎'
            ,'kumamoto':u'熊本'
            ,'oita':u'大分'
            ,'miyazaki':u'宮崎'
            ,'kagoshima':u'鹿児島'
        }
        return areas[keyword]
