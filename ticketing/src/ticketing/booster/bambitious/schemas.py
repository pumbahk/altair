# -*- coding:utf-8 -*-
from ..schemas import Form
from wtforms import fields
from wtforms import validators as v
from wtforms import ValidationError

from ticketing.master.models import Prefecture
from .. import fields as my_fields
from ticketing.formhelpers import text_type_but_none_if_not_given, Zenkaku, Katakana, NFKC, lstrip, strip, strip_hyphen, strip_spaces, SejCompliantEmail, CP932
from datetime import date


from ..widgets import ymd_widget, radio_list_widget, get_year_choices, get_year_months, get_year_days

class OrderFormSchema(Form):
    def validate_day(self, field):
        try:
            date(int(self.year.data), int(self.month.data), int(self.day.data))
        except ValueError:
            raise ValidationError(u'日付が正しくありません')

    def validate_tel_2(self, field):
        if not self.tel_1.data and not self.tel_2.data:
            raise ValidationError(u'電話番号は自宅か携帯かどちらかを入力してください')

    # 新規・継続
    cont = fields.RadioField(u"新規／継続", validators=[v.Required()], choices=[('no', u'新規'),('yes', u'継続')], widget=radio_list_widget)
    member_type = fields.SelectField(u"会員種別選択", validators=[v.Required()])
    t_shirts_size = fields.SelectField(u"ブースターシャツサイズ", choices=[('L', u'L'),('3L', u'3L')], validators=[v.Optional()], coerce=text_type_but_none_if_not_given)
    first_name = fields.TextField(u"氏名", filters=[strip_spaces], validators=[v.Required(), Zenkaku])
    last_name = fields.TextField(u"氏名", filters=[strip_spaces], validators=[v.Required(),Zenkaku])
    first_name_kana = fields.TextField(u"氏名(カナ)", filters=[strip_spaces, NFKC], validators=[v.Required(),Katakana])
    last_name_kana = fields.TextField(u"氏名(カナ)", filters=[strip_spaces, NFKC], validators=[v.Required(),Katakana])
    year = my_fields.StringFieldWithChoice(u"誕生日", filters=[strip_spaces], choices=get_year_choices(), widget=ymd_widget)
    month = my_fields.StringFieldWithChoice(u"誕生日", filters=[strip_spaces, lstrip('0')], validators=[v.Required()], choices=get_year_months(), widget=ymd_widget)
    day = my_fields.StringFieldWithChoice(u"誕生日", filters=[strip_spaces, lstrip('0')], validators=[v.Required()], choices=get_year_days(), widget=ymd_widget)
    sex = fields.RadioField(u"性別", validators=[v.Required()], choices=[('male', u'男性'),('female', u'女性')], widget=radio_list_widget)
    zipcode1 = fields.TextField(u"郵便番号", validators=[v.Required(), v.Regexp(r'\d{3}')])
    zipcode2 = fields.TextField(u"郵便番号", validators=[v.Required(), v.Regexp(r'\d{4}')])
    prefecture = fields.SelectField(u"都道府県", validators=[v.Required(), CP932], choices=[(p.name, p.name)for p in Prefecture.all()], default=u'宮城県')
    city = fields.TextField(u"市区町村", filters=[strip_spaces], validators=[v.Required(), CP932])
    address1 = fields.TextField(u"住所", filters=[strip_spaces], validators=[v.Required(), CP932])
    address2 = fields.TextField(u"住所", filters=[strip_spaces], validators=[CP932])
    tel_1 = fields.TextField(u"電話番号(携帯)", filters=[strip_spaces], validators=[v.Length(max=11), v.Regexp(r'^\d*$', message=u'-を抜いた数字のみを入力してください')])
    tel_2 = fields.TextField(u"電話番号(自宅)", filters=[strip_spaces], validators=[v.Length(max=11), v.Regexp(r'^\d*$', message=u'-を抜いた数字のみを入力してください')])
    fax = fields.TextField(u"FAX番号", filters=[strip_spaces], validators=[v.Length(max=11), v.Regexp(r'^\d*$', message=u'-を抜いた数字のみを入力してください')])
    email_1 = fields.TextField(u"メールアドレス", filters=[strip_spaces], validators=[v.Required(), SejCompliantEmail()])
    email_1_confirm = fields.TextField(u"メールアドレス（確認用）", filters=[strip_spaces], validators=[v.Required(), SejCompliantEmail(), v.EqualTo('email_1', u'確認用メールアドレスが一致しません。')])

    product_delivery_method = fields.SelectField(label=u"会員特典受け取り方法", validators=[v.Required()], choices=[])
    
class OrderReviewSchema(Form):
    order_no = fields.TextField(u"注文番号", filters=[strip_spaces], validators=[v.Required()])
    tel = fields.TextField(u"電話番号", filters=[strip_spaces, strip_hyphen()], validators=[v.Required()])

