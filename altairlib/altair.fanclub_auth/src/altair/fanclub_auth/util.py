# -*- coding:utf-8 -*-
from datetime import datetime as dt

PREFECTURE = {
    '01': u'北海道',
    '02': u'青森県',
    '03': u'岩手県',
    '04': u'宮城県',
    '05': u'秋田県',
    '06': u'山形県',
    '07': u'福島県',
    '08': u'茨城県',
    '09': u'栃木県',
    '10': u'群馬県',
    '11': u'埼玉県',
    '12': u'千葉県',
    '13': u'東京都',
    '14': u'神奈川県',
    '15': u'新潟県',
    '16': u'富山県',
    '17': u'石川県',
    '18': u'福井県',
    '19': u'山梨県',
    '20': u'長野県',
    '21': u'岐阜県',
    '22': u'静岡県',
    '23': u'愛知県',
    '24': u'三重県',
    '25': u'滋賀県',
    '26': u'京都府',
    '27': u'大阪府',
    '28': u'兵庫県',
    '29': u'奈良県',
    '30': u'和歌山県',
    '31': u'鳥取県',
    '32': u'島根県',
    '33': u'岡山県',
    '34': u'広島県',
    '35': u'山口県',
    '36': u'徳島県',
    '37': u'香川県',
    '38': u'愛媛県',
    '39': u'高知県',
    '40': u'福岡県',
    '41': u'佐賀県',
    '42': u'長崎県',
    '43': u'熊本県',
    '44': u'大分県',
    '45': u'宮崎県',
    '46': u'鹿児島県',
    '47': u'沖縄県'
}


class FanclubMetaDataConvertUtil(object):
    @staticmethod
    def prefeture_code_to_str(code):
        if code:
            return PREFECTURE.get(code, u'')

