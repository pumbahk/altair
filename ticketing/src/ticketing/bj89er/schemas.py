# -*- coding:utf-8 -*-
from wtforms import Form
from wtforms import fields
from wtforms import validators as v

# TODO: メールアドレスの一致確認
# TODO: 郵便番号、電話番号のパターンチェック

class Schema(Form):
    # 新規・継続
    cont = fields.TextField(u"新規／継続", validators=[v.required()])
    member_type = fields.TextField(u"会員種別選択")
    number = fields.IntegerField(u"口数選択")
    first_name = fields.TextField(u"氏名")
    last_name = fields.TextField(u"氏名")
    first_name_kana = fields.TextField(u"氏名(カナ)")
    last_name_kana = fields.TextField(u"氏名(カナ)")
    year = fields.IntegerField(u"誕生日", validators=[v.required()])
    month = fields.IntegerField(u"誕生日", validators=[v.required()])
    day = fields.IntegerField(u"誕生日", validators=[v.required()])
    sex = fields.TextField(u"性別", validators=[v.required()])
    zipcode1 = fields.TextField(u"郵便番号")
    zipcode2 = fields.TextField(u"郵便番号")
    prefecture = fields.TextField(u"都道府県")
    city = fields.TextField(u"市区町村")
    address1 = fields.TextField(u"住所")
    address2 = fields.TextField(u"住所")
    tel1_1 = fields.TextField(u"電話番号(携帯)")
    tel1_2 = fields.TextField(u"電話番号(携帯)")
    tel1_3 = fields.TextField(u"電話番号(携帯)")
    tel2_1 = fields.TextField(u"電話番号(自宅)")
    tel2_2 = fields.TextField(u"電話番号(自宅)")
    tel2_3 = fields.TextField(u"電話番号(自宅)")
    email = fields.TextField(u"メールアドレス")
    email2 = fields.TextField(u"メールアドレス（確認用）")
