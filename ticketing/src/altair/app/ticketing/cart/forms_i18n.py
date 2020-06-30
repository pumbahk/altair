# -*- coding:utf-8 -*-
from altair.formhelpers.translations import Translations
from altair.formhelpers.form import OurForm, OurDynamicForm
from wtforms.validators import Regexp, Length, Optional, EqualTo, AnyOf, ValidationError
from altair.formhelpers.validators import (
    Required,
    Phone,
    Zenkaku,
    Katakana,
    SejCompliantEmail,
    CP932,
    SwitchOptional,
    DynSwitchDisabled,
    after1900,
    )
from altair.formhelpers.fields.core import (
    OurTextField,
    OurEmailField,
    OurRadioField,
    OurBooleanField,
    OurSelectField,
    OurIntegerField,
    OurFormField,
    )
from altair.formhelpers.fields import (
    OurDateField
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
    OurDateWidget,
    build_date_input_select_japanese_japan,
    build_date_input_select_i18n,
    )
from altair.app.ticketing.users.models import SexEnum
from .schemas import length_limit_for_sej, japanese_prefecture_select_input
from altair.app.ticketing.i18n import custom_locale_negotiator
import forms_i18n_helper as h

class ClientFormFactory(object):
    def __init__(self, request):
        self._ = request.translate
        self.locale_name = request.locale_name
        self.request = request

    def get_countries(self):
        return h.get_countries(self.request)

    def make_form(self):
        _ = self._
        request = self.request
        locale_name = self.locale_name
        countries = self.get_countries()
        class ClientForm(OurDynamicForm):
            def _get_translations(self):
                return Translations()

            last_name = OurTextField(
                label=_(u"姓"),
                note=_(u"(全角)") + _(u"パスポートと一致しているものを入力してください"),
                filters=[strip_spaces],
                validators=h.last_name_validators(request)
                )
            last_name_kana = OurTextField(
                label=_(u"姓(カナ)"),
                note=_(u"(全角カナ)"),
                filters=[strip_spaces, NFKC],
                validators=[
                    Required(_(u'入力してください')),
                    Katakana,
                    length_limit_for_sej,
                    ]
                ) if locale_name == 'ja' or not request.organization.setting.i18n else None
            first_name = OurTextField(
                label=_(u"名"),
                note=_(u"(全角)") + _(u"パスポートと一致しているものを入力してください"),
                filters=[strip_spaces],
                validators=h.first_name_validators(request)
                )
            first_name_kana = OurTextField(
                label=_(u"名(カナ)"),
                note=_(u"(全角カナ)"),
                filters=[strip_spaces, NFKC],
                validators=[
                    Required(_(u'入力してください')),
                    Katakana,
                    length_limit_for_sej,
                    ]
                ) if locale_name == 'ja' or not request.organization.setting.i18n else None
            tel_1 = OurTextField(
                label=_(u"電話番号"),
                note=_(u"例: 080xxxxyyyy"),
                filters=[ignore_space_hyphen, NFKC],
                validators=[
                    SwitchOptional('tel_2'),
                    Required(_(u'入力してください')),
                    Length(min=1, max=11),
                    Regexp(r'^\d*$', message=_(u'-(ハイフン)を抜いた半角数字のみを入力してください')),
                    ]
                )
            tel_2 = OurTextField(
                label=_(u"電話番号 (携帯)"),
                note=_(u"例: 080xxxxyyyy"),
                filters=[ignore_space_hyphen, NFKC],
                validators=[
                    Optional(),
                    Length(min=1, max=11),
                    Regexp(r'^\d*$', message=_(u'-(ハイフン)を抜いた半角数字のみを入力してください')),
                    ]
                )
            fax = OurTextField(
                label=_(u"FAX番号"),
                note=_(u"-(ハイフン)を抜いた半角数字のみを入力してください"),
                filters=[ignore_space_hyphen, NFKC],
                validators=[
                    Optional(),
                    Length(min=1, max=11),
                    Phone(_(u'確認してください')),
                    ]
                )
            zip = OurTextField(
                label=_(u"郵便番号"),
                filters=[ignore_space_hyphen, NFKC],
                validators=h.zip_validators(request),
                note=_(u'半角英数7ケタ')
                )
            country = OurSelectField(
                label=_(u"国・地域"),
                filters=[strip_spaces],
                validators=[
                    Required(_(u"入力してください")),
                    AnyOf(countries, message=_(u"リストから選択してください。"))
                    ]
                ) if request.organization.setting.i18n else None
            prefecture = OurTextField(
                label=_(u"都道府県"),
                filters=[strip_spaces],
                validators=h.prefecture_validators(request),
                )
            city = OurTextField(
                label=_(u"市区町村"),
                filters=[strip_spaces],
                validators=h.city_validators(request)
            )
            address_1 = OurTextField(
                label=_(u"町名番地"),
                filters=[strip_spaces],
                validators=h.address_1_validators(request)
                )
            address_2 = OurTextField(
                label=_(u"建物名等"),
                filters=[strip_spaces],
                validators=h.address_2_validators(request)
                )
            email_1 = OurEmailField(
                label=_(u"メールアドレス"),
                note=_(u"半角英数"),
                filters=[strip_spaces, NFKC],
                description=lambda field: field._form.context.request.view_context.mail_filter_domain_notice if hasattr(field._form.context.request, 'view_context') else u'',
                validators=h.required_mail_validators(request)
                )
            email_1_confirm = OurEmailField(
                label=_(u"確認用"),
                filters=[strip_spaces, NFKC],
                validators=h.required_mail_validators(request)
                )
            # XXX: 黒魔術的。email_2 に値が入っていて email_1 に値が入っていなかったら、email_1 に値を移すという動作をする
            email_2 = Liaison(
                email_1,
                OurEmailField(
                    label=_(u"メールアドレス"),
                    filters=[strip_spaces, NFKC],
                    validators=h.mail_validators(request)
                    )
                )
            # XXX: 黒魔術的。email_2_confirm に値が入っていて email_1_confirm に値が入っていなかったら、email_1 に値を移すという動作をする
            email_2_confirm = Liaison(
                email_1_confirm,
                OurEmailField(
                    label=_(u"確認用"),
                    filters=[strip_spaces, NFKC],
                    validators=h.mail_validators(request)
                    )
                )

            sex = OurRadioField(_(u'性別'), choices=[(str(SexEnum.Male), _(u'男性')), (str(SexEnum.Female), _(u'女性'))], default=str(SexEnum.Female))
            birthday = OurDateField(
                label=_(u"誕生日"),
                value_defaults={'year': u'1980'},
                missing_value_defaults={'year': u'', 'month': u'', 'day': u'', },
                widget=OurDateWidget(
                    input_builder=build_date_input_select_i18n
                        if custom_locale_negotiator(request) != u'ja' else build_date_input_select_japanese_japan
                ),
                validators=[
                    after1900,
                ]
            )

            def __init__(self, formdata=None, obj=None, prefix=u'', **kwargs):
                context = kwargs.pop('context')
                self.context = context
                flavors = kwargs.pop('flavors', {})
                super(ClientForm, self).__init__(formdata, obj, prefix, **kwargs)
                if flavors.get('japanese_prefectures', False):
                    self.prefecture.widget = japanese_prefecture_select_input
                self.mobile_and_landline_phone_number = flavors.get('mobile_and_landline_phone_number', False)
                self.pc_and_mobile_email_address = flavors.get('pc_and_mobile_email_address', False)

            def validate_tel_2(self, field):
                if not self.tel_1.data and not self.tel_2.data:
                    raise ValidationError(_(u'電話番号は自宅か携帯かどちらかを入力してください'))

            def _validate_email_addresses(self, *args, **kwargs):
                status = True
                data = self.data
                if data["email_1"] != data["email_1_confirm"]:
                    getattr(self, "email_1").errors.append(_(u"メールアドレスと確認メールアドレスが一致していません。"))
                    status = False
                if data["email_2"] != data["email_2_confirm"]:
                    getattr(self, "email_2").errors.append(_(u"メールアドレスと確認メールアドレスが一致していません。"))
                    status = False
                return status

            def validate_birthday(self, field):
                if self.context.request.organization.code in ['RT', 'PH', 'KU', 'IK', 'CC', 'AC', 'FE', 'GF', 'RL'] \
                        and not self.birthday.data:
                    self.birthday.errors.append(u"選択してください。")
                    return False
                return True

            def validate_sex(self, field):
                if self.context.request.organization.code in ['RT', 'PH', 'KU', 'IK', 'CC', 'AC', 'FE', 'GF', 'RL'] \
                        and not self.sex.data:
                    self.sex.errors.append(u"選択してください。")
                    return False
                return True

            def validate(self, *args, **kwargs):
                # このように and 演算子を展開しないとすべてが一度に評価されない
                status = super(ClientForm, self).validate()
                status = self._validate_email_addresses() and status
                return status

        return ClientForm
