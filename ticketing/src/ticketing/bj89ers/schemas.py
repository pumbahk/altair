# -*- coding:utf-8 -*-
from wtforms import Form
from wtforms import fields
from wtforms import validators as v

class Schema(Form):
    # 新規・継続
    cont = fields.TextField(u"新規／継続", validators=[v.Required()])
    member_type = fields.TextField(u"会員種別選択", validators=[v.Required()])
    #number = fields.IntegerField(u"口数選択", validators=[v.Required()])
    first_name = fields.TextField(u"氏名", validators=[v.Required()])
    last_name = fields.TextField(u"氏名", validators=[v.Required()])
    first_name_kana = fields.TextField(u"氏名(カナ)", validators=[v.Required()])
    last_name_kana = fields.TextField(u"氏名(カナ)", validators=[v.Required()])
    year = fields.IntegerField(u"誕生日", validators=[v.Required()])
    month = fields.IntegerField(u"誕生日", validators=[v.Required()])
    day = fields.IntegerField(u"誕生日", validators=[v.Required()])
    sex = fields.TextField(u"性別", validators=[v.Required()])
    zipcode1 = fields.TextField(u"郵便番号", validators=[v.Required(), v.Regexp(r'\d{3}')])
    zipcode2 = fields.TextField(u"郵便番号", validators=[v.Required(), v.Regexp(r'\d{4}')])
    prefecture = fields.TextField(u"都道府県", validators=[v.Required()])
    city = fields.TextField(u"市区町村", validators=[v.Required()])
    address1 = fields.TextField(u"住所", validators=[v.Required()])
    address2 = fields.TextField(u"住所")
    tel1_1 = fields.TextField(u"電話番号(携帯)", validators=[v.Regexp(r'\d*')])
    tel1_2 = fields.TextField(u"電話番号(携帯)", validators=[v.Regexp(r'\d*')])
    tel1_3 = fields.TextField(u"電話番号(携帯)", validators=[v.Regexp(r'\d*')])
    tel2_1 = fields.TextField(u"電話番号(自宅)", validators=[v.Regexp(r'\d*')])
    tel2_2 = fields.TextField(u"電話番号(自宅)", validators=[v.Regexp(r'\d*')])
    tel2_3 = fields.TextField(u"電話番号(自宅)", validators=[v.Regexp(r'\d*')])
    email = fields.TextField(u"メールアドレス", validators=[v.Email()])
    email2 = fields.TextField(u"メールアドレス（確認用）", validators=[v.Email(), v.EqualTo('email')])
    publicity = fields.TextField(u"媒体への掲載希望", validators=[v.AnyOf("yes", "no")])
    nickname = fields.TextField(u"媒体掲載時のニックネーム")
