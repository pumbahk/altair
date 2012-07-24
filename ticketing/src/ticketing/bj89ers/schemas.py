# -*- coding:utf-8 -*-
from wtforms import Form
from wtforms import fields
from wtforms import widgets
from wtforms import validators as v
from wtforms.ext.i18n.utils import DefaultTranslations
from wtforms import ValidationError

from ticketing.master.models import Prefecture
from ticketing.core import models as c_models
from datetime import date, datetime
import unicodedata
from ticketing.formhelpers import Translations

from . import fields as my_fields
from . import widgets as my_widgets

import re

ymd_widget = my_widgets.Switcher(
    'select',
    select=widgets.Select(),
    input=widgets.TextInput()
    )

radio_list_widget = my_widgets.Switcher(
    'list',
    list=widgets.ListWidget(prefix_label=False),
    plain=my_widgets.GenericSerializerWidget(prefix_label=False)
    )

def text_type_but_none_if_not_given(value):
    return unicode(value) if value is not None else None

def get_year_choices():
    current_year = datetime.now().year
    years =  [(str(year), year) for year in range(current_year-100, current_year)]
    return years

def get_year_months():
    months =  [(str(month), month) for month in range(1,13)]
    return months

def get_year_days():
    days =  [(str(month), month) for month in range(1,32)]
    return days

Zenkaku = v.Regexp(r"^[^\x01-\x7f]+$", message=u'全角で入力してください')
Katakana = v.Regexp(ur'^[ァ-ヶ]+$', message=u'カタカナで入力してください')

def NFKC(unistr):
    return unistr and unicodedata.normalize('NFKC', unistr)

def lstrip(chars):
    def stripper(unistr):
        return unistr and unistr.lstrip(chars)
    return stripper

def strip(chars):
    def stripper(unistr):
        return unistr and unistr.strip(chars)
    return stripper

REGEX_HYPHEN = re.compile('\-')
def strip_hyphen():
    def stripper(unistr):
        print unistr
        return unistr and REGEX_HYPHEN.sub('', unistr)
    return stripper

strip_spaces = strip(u' 　')

class OrderFormSchema(Form):

    def _get_translations(self):
        return Translations({
            'This field is required.' : u'入力してください',
            'Not a valid choice' : u'選択してください',
            'Invalid email address.' : u'Emailの形式が正しくありません。',
            'Invalid input.' : u'入力が正しくありません',
        })

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
    t_shirts_size = fields.SelectField(u"Tシャツサイズ", choices=[('L', u'L'),('3L', u'3L')], validators=[v.Optional()], coerce=text_type_but_none_if_not_given)
    #number = fields.IntegerField(u"口数選択", validators=[v.Required()])
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
    prefecture = fields.SelectField(u"都道府県", validators=[v.Required()], choices=[(p.name, p.name)for p in Prefecture.all()], default=u'宮城県')
    city = fields.TextField(u"市区町村", filters=[strip_spaces], validators=[v.Required()])
    address1 = fields.TextField(u"住所", filters=[strip_spaces], validators=[v.Required()])
    address2 = fields.TextField(u"住所", filters=[strip_spaces])
    tel_1 = fields.TextField(u"電話番号(携帯)", filters=[strip_spaces], validators=[v.Regexp(r'^\d*$', message=u'-を抜いた数字のみを入力してください')])
    tel_2 = fields.TextField(u"電話番号(自宅)", filters=[strip_spaces], validators=[v.Regexp(r'^\d*$', message=u'-を抜いた数字のみを入力してください')])
    email = fields.TextField(u"メールアドレス", filters=[strip_spaces], validators=[v.Email()])
    email2 = fields.TextField(u"メールアドレス（確認用）", filters=[strip_spaces], validators=[v.Email(), v.EqualTo('email', u'確認用メールアドレスが一致しません。')])
    publicity = fields.SelectField(u"媒体への掲載希望", validators=[v.Optional()], choices=[('yes', u'希望する'),('no', u'希望しない')], coerce=text_type_but_none_if_not_given)
    mail_permission = fields.BooleanField(u"メルマガ配信", default=True)

class OrderReviewSchema(Form):
    order_no = fields.TextField(u"注文番号", filters=[strip_spaces], validators=[v.Required()])
    tel = fields.TextField(u"電話番号", filters=[strip_spaces, strip_hyphen()], validators=[v.Required()])
