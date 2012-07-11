# -*- coding:utf-8 -*-
from wtforms import Form
from wtforms import fields
from wtforms import widgets
from wtforms import validators as v
from wtforms.ext.i18n.utils import DefaultTranslations

from ticketing.master.models import Prefecture
from ticketing.core import models as c_models
from datetime import datetime
import unicodedata

from . import fields as my_fields
from . import widgets as my_widgets

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

messages = {
    'This field is required.' : u'入力してください',
    'Not a valid choice' : u'選択してください',
    'Invalid email address.' : u'Emailの形式が正しくありません。'
}

class JananeseTranslations(object):
    def ugettext(self, string):
        return messages.get(string, '=')

    def ungettext(self, singular, plural, n):
        if n == 1:
            return singular
        return plural

Zenkaku = v.Regexp(r"^[^\x01-\x7f]+$", message=u'全角で入力してください')
Katakana = v.Regexp(ur'^[ァ-ヶ]+$', message=u'カタカナで入力してください')

def NFKC(unistr):
    return unistr and unicodedata.normalize('NFKC', unistr)

class OrderFormSchema(Form):

    def _get_translations(self):
        return DefaultTranslations(JananeseTranslations())

    # 新規・継続
    cont = fields.RadioField(u"新規／継続", validators=[v.Required()], choices=[('no', u'新規'),('yes', u'継続')], widget=radio_list_widget)
    old_id_number = fields.TextField(u"会員番号", validators=[v.Regexp(r'\d{8}', message=u'半角数字8ケタで入力してください。'), v.Optional()])
    member_type = fields.SelectField(u"会員種別選択", validators=[v.Required()])
    t_shirts_size = fields.SelectField(u"Tシャツサイズ", choices=[('L', u'L'),('3L', u'3L')], validators=[v.Optional()])
    #number = fields.IntegerField(u"口数選択", validators=[v.Required()])
    first_name = fields.TextField(u"氏名", validators=[v.Required(), Zenkaku])
    last_name = fields.TextField(u"氏名", validators=[v.Required(),Zenkaku])
    first_name_kana = fields.TextField(u"氏名(カナ)", filters=[NFKC], validators=[v.Required(),Katakana])
    last_name_kana = fields.TextField(u"氏名(カナ)", filters=[NFKC], validators=[v.Required(),Katakana])
    year = my_fields.StringFieldWithChoice(u"誕生日", choices=get_year_choices(), widget=ymd_widget)
    month = my_fields.StringFieldWithChoice(u"誕生日", validators=[v.Required()], choices=get_year_months(), widget=ymd_widget)
    day = my_fields.StringFieldWithChoice(u"誕生日", validators=[v.Required()], choices=get_year_days(), widget=ymd_widget)
    sex = fields.RadioField(u"性別", validators=[v.Required()], choices=[('male', u'男性'),('female', u'女性')], widget=radio_list_widget)
    zipcode1 = fields.TextField(u"郵便番号", validators=[v.Required(), v.Regexp(r'\d{3}')])
    zipcode2 = fields.TextField(u"郵便番号", validators=[v.Required(), v.Regexp(r'\d{4}')])
    prefecture = fields.SelectField(u"都道府県", validators=[v.Required()], choices=[(p.name, p.name)for p in Prefecture.all()], default=u'宮城県')
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
    email2 = fields.TextField(u"メールアドレス（確認用）", validators=[v.Email(), v.EqualTo('email', u'確認用メールアドレスが一致しません。')])
    publicity = fields.SelectField(u"媒体への掲載希望", validators=[v.Required()], choices=[('yes', u'希望する'),('no', u'希望しない')])
    mail_permission = fields.BooleanField(u"メルマガ配信", default=True)
    nickname = fields.TextField(u"媒体掲載時のニックネーム")

    def validate_nickname(self, form):
        if self.publicity.data == 'yes' and not form.data:
            from wtforms.validators import ValidationError
            raise ValidationError(u'ニックネームを入力してください。')


class OrderReviewSchema(Form):
    order_no = fields.TextField(u"オーダー番号", validators=[v.Required()])
    tel = fields.TextField(u"電話番号", validators=[v.Required()])
