# -*- coding:utf-8 -*-

from datetime import datetime
from wtforms.ext.csrf.session import SessionSecureForm
from wtforms.validators import Regexp, Length, Optional, EqualTo
from wtforms.widgets import Select as OurSelect
from markupsafe import Markup
from altair.formhelpers.form import OurForm, OurDynamicForm
from altair.formhelpers.translations import Translations
from altair.formhelpers.validators import (
    Required,
    Phone,
    Zenkaku,
    Katakana,
    SejCompliantEmail,
    CP932,
    SwitchOptional,
    DynSwitchDisabled,
    )
from altair.formhelpers.fields.datetime import (
    OurDateField,
    )
from altair.formhelpers.fields.core import (
    OurTextField,
    OurRadioField,
    OurBooleanField,
    OurSelectField,
    OurIntegerField,
    OurFormField,
    )
from altair.formhelpers.fields.liaison import (
    Liaison,
    )
from altair.formhelpers.filters import (
    strip_spaces,
    ignore_space_hyphen,
    text_type_but_none_if_not_given,
    NFKC,
    lstrip,
    )
from altair.formhelpers.widgets import (
    OurTextInput,
    OurListWidget,
    GenericSerializerWidget,
    OurDateWidget,
    OurSelectInput,
    OurCheckboxInput,
    )
from altair.app.ticketing.master.models import Prefecture
from .helpers import SwitchingMarkup
from .view_support import build_dynamic_form, build_date_input_select

length_limit_for_sej = Length(max=10, message=u'10文字以内で入力してください')
length_limit_long = Length(max=255, message=u'255文字以内で入力してください')

japanese_prefecture_select_input = OurSelectInput(choices=[(p.name, p.name) for p in Prefecture.all()])

class CSRFSecureForm(SessionSecureForm):
    SECRET_KEY = 'EPj00jpfj8Gx1SjnyLxwBBSQfnQ9DJYe0Ym'

def normalize_point_account_number(value):
    import re
    if value is not None and re.match(r'^\d{16}$', value):
        return '%s-%s-%s-%s' % (value[0:4], value[4:8], value[8:12], value[12:16])
    return value

class PointForm(OurForm):
    accountno = OurTextField(
        label=u"楽天スーパーポイント口座",
        filters=[NFKC, normalize_point_account_number],
        validators=[
            Optional(),
            Regexp(r'^(?:\d{4}-\d{4}-\d{4}-\d{4}|\d{16})$', message=u'16桁の数字を入れて下さい。'),
        ]
    )

class ClientForm(OurDynamicForm):
    def _get_translations(self):
        return Translations()

    last_name = OurTextField(
        label=u"姓",
        note=u"(全角)",
        filters=[strip_spaces],
        validators=[
            Required(),
            Zenkaku,
            length_limit_for_sej,
            ],
        )
    last_name_kana = OurTextField(
        label=u"姓(カナ)",
        note=u"(全角カナ)",
        filters=[strip_spaces, NFKC],
        validators=[
            Required(),
            Katakana,
            length_limit_for_sej,
            ]
        )
    first_name = OurTextField(
        label=u"名",
        note=u"(全角)",
        filters=[strip_spaces],
        validators=[
            Required(),
            Zenkaku,
            length_limit_for_sej,
            ]
        )
    first_name_kana = OurTextField(
        label=u"名(カナ)",
        note=u"(全角カナ)",
        filters=[strip_spaces, NFKC],
        validators=[
            Required(),
            Katakana,
            length_limit_for_sej,
            ]
        )
    tel_1 = OurTextField(
        label=u"電話番号",
        note=u"(例:09012341234)",
        filters=[ignore_space_hyphen, NFKC],
        validators=[
            SwitchOptional('tel_2'),
            Required(),
            Length(min=1, max=11),
            Regexp(r'^\d*$', message=u'-(ハイフン)を抜いた半角数字のみを入力してください'),
            ]
        )
    tel_2 = OurTextField(
        label=u"電話番号 (携帯)",
        note=u"(例:09012341234)",
        filters=[ignore_space_hyphen, NFKC],
        validators=[
            Optional(),
            Length(min=1, max=11),
            Regexp(r'^\d*$', message=u'-(ハイフン)を抜いた半角数字のみを入力してください'),
            ]
        )
    fax = OurTextField(
        label=u"FAX番号",
        note=u"(ハイフンを除いてご入力ください)",
        filters=[ignore_space_hyphen, NFKC],
        validators=[
            Optional(),
            Length(min=1, max=11),
            Phone(u'FAX番号を確認してください'),
            ]
        )
    zip = OurTextField(
        label=u"郵便番号",
        filters=[ignore_space_hyphen, NFKC],
        validators=[
            Required(),
            Regexp(r'^\d{7}$', message=u'-(ハイフン)を抜いた半角数字(7桁)のみを入力してください'),
            Length(min=7, max=7, message=u'確認してください'),
            ],
        note=u'(半角英数7ケタ)'
        )
    prefecture = OurTextField(
        label=u"都道府県",
        filters=[strip_spaces],
        validators=[
            Required()
            ]
        )
    city = OurTextField(
        label=u"市区町村",
        filters=[strip_spaces],
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
            CP932,
        ]
    )
    address_1 = OurTextField(
        label=u"町名番地",
        filters=[strip_spaces],
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
            CP932,
            ]
        )
    address_2 = OurTextField(
        label=u"建物名等",
        filters=[strip_spaces],
        validators=[
            Length(max=255, message=u'255文字以内で入力してください'),
            CP932,
            ]
        )
    email_1 = OurTextField(
        label=u"メールアドレス",
        note=u"(半角英数)",
        filters=[strip_spaces, NFKC],
        description=lambda field: field._form.context.request.view_context.mail_filter_domain_notice if hasattr(field._form.context.request, 'view_context') else u'',
        validators=[
            Required(),
            SejCompliantEmail(),
            ]
        )
    email_1_confirm = OurTextField(
        label=u"メールアドレス (確認)",
        filters=[strip_spaces, NFKC],
        validators=[
            Required(),
            SejCompliantEmail(),
            ]
        )
    # XXX: 黒魔術的。email_2 に値が入っていて email_1 に値が入っていなかったら、email_1 に値を移すという動作をする
    email_2 = Liaison(
        email_1,
        OurTextField(
            label=u"メールアドレス",
            filters=[strip_spaces, NFKC],
            validators=[
                SejCompliantEmail(),
                ]
            )
        )
    # XXX: 黒魔術的。email_2_confirm に値が入っていて email_1_confirm に値が入っていなかったら、email_1 に値を移すという動作をする
    email_2_confirm = Liaison(
        email_1_confirm,
        OurTextField(
            label=u"メールアドレス (確認)",
            filters=[strip_spaces, NFKC],
            validators=[
                SejCompliantEmail(),
                ]
            )
        )

    def __init__(self, formdata=None, obj=None, prefix=u'', **kwargs):
        context = kwargs.pop('context')
        self.context = context
        flavors = kwargs.pop('flavors', {})
        super(ClientForm, self).__init__(formdata, obj, prefix, **kwargs)
        if flavors.get('japanese_prefectures', False):
            self.prefecture.widget = japanese_prefecture_select_input

    def validate_tel_2(self, field):
        if not self.tel_1.data and not self.tel_2.data:
            raise ValidationError(u'電話番号は自宅か携帯かどちらかを入力してください')

    def _validate_email_addresses(self, *args, **kwargs):
        status = True
        data = self.data
        if data["email_1"] != data["email_1_confirm"]:
            getattr(self, "email_1").errors.append(u"メールアドレスと確認メールアドレスが一致していません。")
            status = False
        if data["email_2"] != data["email_2_confirm"]:
            getattr(self, "email_2").errors.append(u"メールアドレスと確認メールアドレスが一致していません。")
            status = False
        return status

    def validate(self):
        # このように and 演算子を展開しないとすべてが一度に評価されない
        status = super(ClientForm, self).validate()
        status = self._validate_email_addresses() and status
        return status

def prepend_list(x, xs):
    r = [x]
    r.extend(xs)
    return r

def prepend_validator(field, x):
    field.validators = prepend_list(x, field.validators)

class ExtraForm(OurDynamicForm):
    def __init__(self, *args, **kwargs):
        self._containing_field = kwargs.pop('_containing_field', None)
        super(ExtraForm, self).__init__(*args, **kwargs)

    def _get_translations(self):
        self._containing_field._form._get_translations()
        return self._containing_field._form._get_translations()


class _89ersExtraForm(ExtraForm):
    birthday = OurDateField(
        u"誕生日",
        value_defaults={ 'year': u'1980', },
        missing_value_defaults={ 'year': u'', 'month': u'', 'day': u'', },
        widget=OurDateWidget(
            input_builder=build_date_input_select
            ),
        validators=[Required()]
        )
    sex = OurRadioField(
        u"性別",
        validators=[Required()],
        choices=[('male', u'男性'),('female', u'女性')],
        widget=OurListWidget(prefix_label=False)
        )
    # 新規・継続
    cont = OurRadioField(
        u"新規／継続",
        validators=[Required()],
        choices=[('no', u'新規'),('yes', u'継続')],
        widget=OurListWidget(prefix_label=False)
        )
    old_id_number = OurTextField(
        u"会員番号",
        filters=[strip_spaces, NFKC],
        validators=[
            Regexp(
                r'\d{8}$',
                message=u'半角数字8ケタで入力してください。'
                ),
            DynSwitchDisabled(u'{cont} <> "yes"'),
            ],
        description=Markup(u'[継続]を選択した方は2013-14年の会員番号をご入力ください'),
        note=Markup(u'(半角数字8ケタ)')
        )
    member_type = OurSelectField(
        u"会員種別選択",
        validators=[Required()],
        description=SwitchingMarkup(
            pc_or_smartphone_text=u'<a href="http://www.89ers.jp/booster/index.html" target=”_blank”><span><small>会員種別についてはこちら</small></span></a>',
            mobile_text=u'<a href="http://www.mobile89ers.jp/imode/cgi-bin/pgget.dll?pg=/i/booster/club/cont/club_p01_00">※会員種別についてはこちら</a>'
            )
        )
    t_shirts_size = OurSelectField(
        u"ClubナイナーズＴシャツサイズ",
        choices=[('L', u'L'),('3L', u'3L')],
        description=u"(ゴールド・プラチナ会員のみ)",
        validators=[
            DynSwitchDisabled(u'NOT(OR({member_type}="ゴールドプラン", {member_type}="プラチナプラン"))'),
            ],
        coerce=text_type_but_none_if_not_given)
    publicity = OurSelectField(
        u"メモリアルブックへの氏名掲載希望",
        description=u"(ゴールド・プラチナ会員のみ)",
        validators=[
            DynSwitchDisabled(u'NOT(OR({member_type}="ゴールドプラン", {member_type}="プラチナプラン"))')
            ],
        choices=[
            ('yes', u'希望する'),
            ('no', u'希望しない')
            ],
        coerce=text_type_but_none_if_not_given)
    mail_permission = OurBooleanField(
        u"メルマガ配信",
        default=True,
        widget=OurCheckboxInput(label=u'希望する')
        )
    motivation = OurSelectField(
        u"クラブナイナーズに入会しようと思ったきっかけは？",
        choices=[
            (u"", u"お選びください"),
            (u"継続で入会", u"継続で入会"),
            (u"入会案内のチラシを見て", u"入会案内のチラシを見て"),
            (u"facebookを見て", u"facebookを見て"),
            (u"twitterを見て", u"twitterを見て"),
            (u"友人・知人に勧められて", u"友人・知人に勧められて"),
            (u"メルマガを見て", u"メルマガを見て"),
            (u"新聞・雑誌を見て", u"新聞・雑誌を見て"),
            (u"検索サイトから", u"検索サイトから"),
            (u"その他", u"その他"),
            ],
        validators=[Required()],
        )
    num_times_at_venue = OurIntegerField(
        u"昨シーズンの会場での観戦回数",
        validators=[Optional()]
        )
    official_ball = OurTextField(
        u"オリジナル公式球への記載希望名",
        description=u"(プラチナ会員のみ)",
        filters=[strip_spaces, NFKC],
        validators=[
            Regexp(r'^\S{1,10}$', message=u'最大10文字'),
            DynSwitchDisabled(u'NOT({member_type}="プラチナプラン")')
            ],
        note=u"（最大10文字）"
        )

    def configure_for_publicity(self):
        prepend_validator(self.publicity, Required())

    def configure_for_t_shirts_size(self):
        prepend_validator(self.t_shirts_size, Required())

    def configure_for_official_ball(self):
        prepend_validator(self.official_ball, Required())
        prepend_validator(self.official_ball, Regexp(u'^\S{1,10}$$', message=u'最大10文字'),)

    def configure_coupon(self):
        prepend_validator(self.coupon, Required())


class BambitiousExtraForm(ExtraForm):
    birthday = OurDateField(
        u"誕生日",
        value_defaults={ 'year': u'1980', },
        missing_value_defaults={ 'year': u'', 'month': u'', 'day': u'', },
        widget=OurDateWidget(
            input_builder=build_date_input_select
            ),
        validators=[Required()]
        )
    sex = OurRadioField(
        u"性別",
        validators=[Required()],
        choices=[('male', u'男性'),('female', u'女性')],
        widget=OurListWidget(prefix_label=False)
        )
    cont = OurRadioField(
        u"新規／継続",
        validators=[Required()],
        choices=[('no', u'新規'),('yes', u'継続')],
        widget=OurListWidget(prefix_label=False)
        )
    old_id_number = OurTextField(
        u"会員番号",
        filters=[strip_spaces, NFKC],
        validators=[
            DynSwitchDisabled(u'{cont} <> "yes"'),
            Regexp(r'\d{7}$', message=u'半角数字7ケタで入力してください。'),
            ],
        description=Markup(u'[継続]を選択した方は2014-2015シーズンの会員番号をご入力ください。<br />継続入会の方で会員種別の変更がない方は、現在お持ちの会員証を引き続きご使用いただきます。'),
        note=Markup(u'(半角数字7ケタ)')
        )
    member_type = OurSelectField(u"会員種別選択", validators=[Required()])

    t_shirts_size_choices = [(x, x) for x in [u"S", u"M", u"L", u"O", u"XO", u"2XO"]]
    t_shirts_size = OurSelectField(
        u"クラブバンビシャスシャツサイズ",
        choices=t_shirts_size_choices,
        description=u"ゴールド会員を選択の方はクラブバンビシャスシャツサイズをお選びください。",
        validators=[
            DynSwitchDisabled(u'NOT({member_type}="ゴールド会員")'),
            ],
        coerce=text_type_but_none_if_not_given
        )
    mail_permission = OurBooleanField(
        u"メルマガ配信",
        default=True,
        widget=OurCheckboxInput(label=u'希望する')
        )

    def product_delivery_method_choices(field):
        context = field._form._containing_field._form.context
        sales_segment = context.available_sales_segments[0]
        return [
            (delivery_method.id, delivery_method.name)
            for delivery_method in set(
                pdmp.delivery_method
                for pdmp in context.available_payment_delivery_method_pairs(sales_segment)
                )
            ]

    product_delivery_method = OurSelectField(
        label=u"会員特典受取方法",
        coerce=long,
        validators=[Required()],
        choices=product_delivery_method_choices,
        note=u"(配送料は無料です。)"
        )

at_least_eighteen = DynSwitchDisabled(u'''
OR(
    YEAR(NOW()) - YEAR({birthday}) > 18,
    AND(
        YEAR(NOW()) - YEAR({birthday}) = 18,
        OR(
            MONTH(NOW()) > MONTH({birthday}),
            AND(
                MONTH(NOW()) = MONTH({birthday}),
                DAY(NOW()) > DAY({birthday})
            )
        )
    )
)''')

class BigbullsExtraForm(ExtraForm):
    birthday = OurDateField(
        u"誕生日",
        value_defaults={ 'year': u'1980', },
        missing_value_defaults={ 'year': u'', 'month': u'', 'day': u'', },
        widget=OurDateWidget(
            input_builder=build_date_input_select
            ),
        validators=[Required()]
        )
    sex = OurRadioField(
        u"性別",
        validators=[Required()],
        choices=[('male', u'男性'),('female', u'女性')],
        widget=OurListWidget(prefix_label=False)
        )
    cont = OurRadioField(
        u"新規／継続",
        validators=[Required()],
        choices=[('no', u'新規'),('yes', u'継続')],
        widget=OurListWidget(prefix_label=False)
        )
    old_id_number = OurTextField(
        u"会員番号",
        filters=[strip_spaces, NFKC],
        validators=[
            Regexp(r'\d+', message=u'半角数字で入力してください。'),
            DynSwitchDisabled(u'{cont} <> "yes"'),
            ],
        description=Markup(u'お分かりの場合、下記に2013-14年の会員番号をご入力ください'),
        note=Markup(u'(会員証記載のアルファベットを除いた半角数字)')
        )
    member_type = OurSelectField(
        u"会員種別選択",
        validators=[Required()],
        description=Markup(u'<a href="http://www.bigbulls.jp/clubbulls.html">会員種別についてはこちら</a>')
        )
    t_shirts_size = OurSelectField(
        u"Tシャツサイズ",
        description=Markup(u"ゴールド会員にお申込の方のみ入力下さい<br/>※サイズをお選びいただけます<br/>"),
        choices=[('L', u'L'),('3L', u'3L'),('5L', u'5L')],
        validators=[
            DynSwitchDisabled(u'NOT({member_type}="ゴールド会員")'),
            ],
        coerce=text_type_but_none_if_not_given,
        )
    parent_first_name = OurTextField(
        u"名",
        filters=[strip_spaces],
        validators=[
            at_least_eighteen,
            Zenkaku,
            length_limit_for_sej
            ]
        )
    parent_last_name = OurTextField(
        u"姓",
        filters=[strip_spaces],
        validators=[
            at_least_eighteen,
            Zenkaku,
            length_limit_for_sej
            ]
        )
    parent_first_name_kana = OurTextField(
        u"名 (カナ)",
        filters=[strip_spaces, NFKC],
        validators=[
            at_least_eighteen,
            Katakana,
            length_limit_for_sej
            ]
        )
    parent_last_name_kana = OurTextField(
        u"姓 (カナ)",
        filters=[strip_spaces, NFKC],
        validators=[
            at_least_eighteen,
            Katakana,
            length_limit_for_sej
            ]
        )
    relationship = OurTextField(
        u"続柄",
        note=u"(例：父、母、など)",
        filters=[strip_spaces],
        validators=[
            at_least_eighteen,
            ]
        )
    mail_permission = OurBooleanField(
        u"【クラブブルズ会員限定】 お得な情報をメールで配信",
        default=True,
        widget=OurCheckboxInput(label=u'希望する')
        )

class DynamicExtraForm(ExtraForm):
    member_type = OurSelectField(
        u"会員種別選択",
        validators=[Required()]
        )

    def __init__(self, *args, **kwargs):
        context = kwargs.get('context')
        fields = build_dynamic_form.unbound_fields(context.cart_setting.extra_form_fields or [])
        super(DynamicExtraForm, self).__init__(*args, _fields=fields, **kwargs)


extra_form_type_map = {
    'booster.89ers': _89ersExtraForm,
    'booster.bambitious': BambitiousExtraForm,
    'booster.bigbulls': BigbullsExtraForm,
    'fc': DynamicExtraForm,
    }
