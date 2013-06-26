# -*- coding:utf-8 -*-
from ..schemas import Form
from wtforms import fields
from wtforms import validators as v
from wtforms import ValidationError

from ticketing.master.models import Prefecture
from .. import fields as my_fields
from ticketing.formhelpers import text_type_but_none_if_not_given, Zenkaku, Katakana, NFKC, lstrip, strip, strip_hyphen, strip_spaces, SejCompliantEmail, CP932
from datetime import date

from ..schemas import length_limit_for_sej, length_limit_long
from ..widgets import ymd_widget, radio_list_widget, get_year_choices, get_year_months, get_year_days

class ExtraForm(Form):
    publicity = fields.SelectField(
        u"ゲームプログラムへのお名前掲載",
        validators=[v.Optional()],
        choices=[
            ('yes', u'希望する'),
            ('no', u'希望しない')
            ],
        coerce=text_type_but_none_if_not_given)

    t_shirts_size = fields.SelectField(u"Tシャツサイズ", 
                                       choices=[('L', u'L'),('3L', u'3L')], 
                                       validators=[v.Optional()], 
                                       coerce=text_type_but_none_if_not_given)
    replica_uniform_size = fields.SelectField(u'レプリカユニフォームサイズ', 
                                              choices=[('S', u'S'), ('M', u'M'), ('L', u'L'),('LL', u'LL'), ('3L', u'3L'), ('4L', u'4L')],
                                              validators=[v.Optional()],
                                              coerce=text_type_but_none_if_not_given)
    authentic_uniform_size = fields.SelectField(u'オーセンティックユニフォームサイズ',
                                                choices=[('S', u'S'), ('M', u'M'), ('L', u'L'),('LL', u'LL'), ('3L', u'3L'), ('4L', u'4L')],
                                                validators=[v.Optional()], 
                                                coerce=text_type_but_none_if_not_given)
    authentic_uniform_color = fields.SelectField(u'オーセンティックユニフォーム色',
                                                choices=[('red', u"赤"), ("white", u"白")],
                                                validators=[v.Optional()], 
                                                coerce=text_type_but_none_if_not_given)
    authentic_uniform_no = fields.IntegerField(u"オーセンティックユニフォーム背番号", validators=[v.Optional(), v.Length(max=2)])
    authentic_uniform_name = fields.TextField(u"オーセンティックユニフォーム名前", validators=[v.Optional(), v.Regexp(r"^[A-Z]+$", message=u"アルファベット大文字のみで入力してください")])

    parent_first_name = fields.TextField(u"氏名", filters=[strip_spaces], validators=[v.Required(), Zenkaku, length_limit_for_sej])
    parent_last_name = fields.TextField(u"氏名", filters=[strip_spaces], validators=[v.Required(),Zenkaku, length_limit_for_sej])
    parent_first_name_kana = fields.TextField(u"氏名(カナ)", filters=[strip_spaces, NFKC], validators=[v.Required(),Katakana, length_limit_for_sej])
    parent_last_name_kana = fields.TextField(u"氏名(カナ)", filters=[strip_spaces, NFKC], validators=[v.Required(),Katakana, length_limit_for_sej])
    relationship = fields.TextField(u"続柄", filters=[strip_spaces], validators=[v.Optional()])
    mail_permission = fields.BooleanField(
        u"【クラブブルズ会員限定】 お得な情報をメールで配信",
        default=True)

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
    old_id_number = fields.TextField(u"会員番号", filters=[strip_spaces], validators=[v.Regexp(r'\d{8}', message=u'半角数字8ケタで入力してください。'), v.Optional()])
    member_type = fields.SelectField(u"会員種別選択", validators=[v.Required()])
    first_name = fields.TextField(u"氏名", filters=[strip_spaces], validators=[v.Required(), Zenkaku, length_limit_for_sej])
    last_name = fields.TextField(u"氏名", filters=[strip_spaces], validators=[v.Required(),Zenkaku, length_limit_for_sej])
    first_name_kana = fields.TextField(u"氏名(カナ)", filters=[strip_spaces, NFKC], validators=[v.Required(),Katakana, length_limit_for_sej])
    last_name_kana = fields.TextField(u"氏名(カナ)", filters=[strip_spaces, NFKC], validators=[v.Required(),Katakana, length_limit_for_sej])
    year = my_fields.StringFieldWithChoice(u"誕生日", filters=[strip_spaces], choices=get_year_choices(), widget=ymd_widget, default=1980)
    month = my_fields.StringFieldWithChoice(u"誕生日", filters=[strip_spaces, lstrip('0')], validators=[v.Required()], choices=get_year_months(), widget=ymd_widget)
    day = my_fields.StringFieldWithChoice(u"誕生日", filters=[strip_spaces, lstrip('0')], validators=[v.Required()], choices=get_year_days(), widget=ymd_widget)
    sex = fields.RadioField(u"性別", validators=[v.Required()], choices=[('male', u'男性'),('female', u'女性')], widget=radio_list_widget)
    zipcode1 = fields.TextField(u"郵便番号", validators=[v.Required(), v.Regexp(r'\d{3}')])
    zipcode2 = fields.TextField(u"郵便番号", validators=[v.Required(), v.Regexp(r'\d{4}')])
    prefecture = fields.SelectField(u"都道府県", validators=[v.Required(), CP932], choices=[(p.name, p.name)for p in Prefecture.all()], default=u'岩手県')
    city = fields.TextField(u"市区町村", filters=[strip_spaces], validators=[v.Required(), CP932, length_limit_long])
    address1 = fields.TextField(u"住所", filters=[strip_spaces], validators=[v.Required(), CP932, length_limit_long])
    address2 = fields.TextField(u"住所", filters=[strip_spaces], validators=[CP932, length_limit_long])
    tel_1 = fields.TextField(u"電話番号(携帯)", filters=[strip_spaces], validators=[v.Length(max=11), v.Regexp(r'^\d*$', message=u'-を抜いた数字のみを入力してください')])
    tel_2 = fields.TextField(u"電話番号(自宅)", filters=[strip_spaces], validators=[v.Length(max=11), v.Regexp(r'^\d*$', message=u'-を抜いた数字のみを入力してください')])
    email_1 = fields.TextField(u"メールアドレス", filters=[strip_spaces], validators=[v.Required(), SejCompliantEmail()])
    email_1_confirm = fields.TextField(u"メールアドレス（確認用）", filters=[strip_spaces], validators=[v.Required(), SejCompliantEmail(), v.EqualTo('email_1', u'確認用メールアドレスが一致しません。')])

    extra = fields.FormField(ExtraForm)

class OrderReviewSchema(Form):
    order_no = fields.TextField(u"注文番号", filters=[strip_spaces], validators=[v.Required()])
    tel = fields.TextField(u"電話番号", filters=[strip_spaces, strip_hyphen()], validators=[v.Required()])
