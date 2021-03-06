# -*- coding:utf-8 -*-
from .mapping import IdNameLabelMapping

PREFECTURE_CHOICES = [
    ## name, label
    ("hokkaido", u'北海道'),
    ("aomori", u'青森県'),
    ("iwate", u'岩手県'),
    ("miyagi", u'宮城県'),
    ("akita", u'秋田県'),
    ("yamagata", u'山形県'),
    ("fukushima", u'福島県'),
    ("ibaraki", u'茨城県'),
    ("tochigi", u'栃木県'),
    ("gunma", u'群馬県'),
    ("saitama", u'埼玉県'),
    ("chiba", u'千葉県'),
    ("tokyo", u'東京都'),
    ("kanagawa", u'神奈川県'),
    ("niigata", u'新潟県'),
    ("toyama", u'富山県'),
    ("ishikawa", u'石川県'),
    ("fukui", u'福井県'),
    ("yamanashi", u'山梨県'),
    ("nagano", u'長野県'),
    ("gifu", u'岐阜県'),
    ("shizuoka", u'静岡県'),
    ("aichi", u'愛知県'),
    ("mie", u'三重県'),
    ("shiga", u'滋賀県'),
    ("kyoto", u'京都府'),
    ("osaka", u'大阪府'),
    ("hyogo", u'兵庫県'),
    ("nara", u'奈良県'),
    ("wakayama", u'和歌山県'),
    ("tottori", u'鳥取県'),
    ("shimane", u'島根県'),
    ("okayama", u'岡山県'),
    ("hiroshima", u'広島県'),
    ("yamaguchi", u'山口県'),
    ("tokushima", u'徳島県'),
    ("kagawa", u'香川県'),
    ("ehime", u'愛媛県'),
    ("kouchi", u'高知県'),
    ("fukuoka", u'福岡県'),
    ("saga", u'佐賀県'),
    ("nagasaki", u'長崎県'),
    ("kumamoto", u'熊本県'),
    ("oita", u'大分県'),
    ("miyazaki", u'宮崎県'),
    ("kagoshima", u'鹿児島県'),
    ("okinawa", u'沖縄県'),
]
PREFECTURE_ENUMS = [(v) for v, _ in PREFECTURE_CHOICES]
PrefectureMapping = IdNameLabelMapping.from_choices(PREFECTURE_CHOICES)
