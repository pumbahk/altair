# -*- coding:utf-8 -*-
from datetime import datetime
from wtforms import fields
from wtforms import validators as v
from wtforms import Form
from wtforms import widgets
from wtforms.validators import Regexp, Length, Optional, EqualTo, AnyOf, ValidationError

from altair.app.ticketing.cart.schemas import ExtraForm, japanese_prefecture_select_input
from altair.app.ticketing.cart.view_support import build_dynamic_form, filter_extra_form_schema
from altair.app.ticketing.users.models import SexEnum
from altair.formhelpers import (
    Required,
    text_type_but_none_if_not_given,
    Zenkaku,
    Katakana,
    NFKC,
    lstrip,
    strip,
    strip_hyphen,
    strip_spaces,
    SejCompliantEmail,
    CP932,
    Translations,
    ignore_space_hyphen,
    )
from altair.formhelpers.fields.liaison import (
    Liaison,
    )
from altair.formhelpers.widgets import (
    OurDateWidget,
    build_date_input_select_japanese_japan,
    build_date_input_select_i18n
    )
from altair.formhelpers.fields import (
    OurDateField
    )
from altair.formhelpers.form import OurForm, OurDynamicForm
from altair.formhelpers.widgets import Switcher
from altair.formhelpers.fields import OurRadioField
from altair.formhelpers.validators import (
    DateTimeFormat,
    after1900,
    SwitchOptional,
    Phone,
    )
from .fields import StringFieldWithChoice
from altair.now import get_now
from altair.formhelpers.fields.core import (
    OurSelectField,
    OurTextField,
    )
import forms_i18n_helper as h
from altair.app.ticketing.cart.schemas import length_limit_for_sej

ymd_widget = Switcher(
    'select',
    select=widgets.Select(),
    input=widgets.TextInput()
    )

class ClientFormFactory(object):
    def __init__(self, request):
        self._ = request.translate
        self.locale_name = request.locale_name
        self.request = request

    def get_countries(self):
        return h.get_countries(self.request)

    def get_client_form_fields(self):
        return h.get_client_form_fields(self.request)

    def make_form(self):
        _ = self._
        request = self.request
        locale_name = self.locale_name
        countries = self.get_countries()
        class ClientForm(OurDynamicForm):
            def _get_translations(self):
                return Translations()

            def __init__(self, formdata=None, obj=None, prefix=u'', **kwargs):
                context = kwargs.pop('context')
                self.context = context
                flavors = kwargs.pop('flavors', {})
                super(ClientForm, self).__init__(formdata, obj, prefix, **kwargs)
                if flavors.get('japanese_prefectures', False):
                    self.prefecture.widget = japanese_prefecture_select_input
                self.mobile_and_landline_phone_number = flavors.get('mobile_and_landline_phone_number', False)
                self.pc_and_mobile_email_address = flavors.get('pc_and_mobile_email_address', False)

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
                ) if locale_name == 'ja' else None
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
                ) if locale_name == 'ja' else None
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
                validators=h.prefecture_validators(request)
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
            email_1 = OurTextField(
                label=_(u"メールアドレス"),
                note=_(u"半角英数"),
                filters=[strip_spaces, NFKC],
                description=lambda field: field._form.context.request.view_context.mail_filter_domain_notice if hasattr(field._form.context.request, 'view_context') else u'',
                validators=h.required_mail_validators(request)
                )
            email_1_confirm = OurTextField(
                label=_(u"確認用"),
                filters=[strip_spaces, NFKC],
                validators=h.required_mail_validators(request)
                )
            # XXX: 黒魔術的。email_2 に値が入っていて email_1 に値が入っていなかったら、email_1 に値を移すという動作をする
            email_2 = Liaison(
                email_1,
                OurTextField(
                    label=_(u"メールアドレス"),
                    filters=[strip_spaces, NFKC],
                    validators=h.mail_validators(request)
                    )
                )
            # XXX: 黒魔術的。email_2_confirm に値が入っていて email_1_confirm に値が入っていなかったら、email_1 に値を移すという動作をする
            email_2_confirm = Liaison(
                email_1_confirm,
                OurTextField(
                    label=_(u"確認用"),
                    filters=[strip_spaces, NFKC],
                    validators=h.mail_validators(request)
                    )
                )
            sex = OurRadioField(_(u'性別'), choices=[(str(SexEnum.Male), _(u'男性')), (str(SexEnum.Female), _(u'女性'))])
            birthday = OurDateField(
                label=_(u"誕生日"),
                value_defaults={'year':u'1980'},
                missing_value_defaults={ 'year': u'', 'month': u'', 'day': u'', },
                widget=OurDateWidget(
                    input_builder=build_date_input_select_i18n
                    ),
                validators=[
                    Required(_(u'入力してください')),
                    after1900,
                    ]
                )
            memo = fields.TextAreaField(_(u"メモ"))

            orion_ticket_phone = OurTextField(
                default=u'',
                validators=[Optional()]
            )

            def get_validated_address_data(self):
                if self.validate():
                    return dict(
                        first_name=self.data['first_name'],
                        last_name=self.data['last_name'],
                        first_name_kana=self.data.get('first_name_kana', u'カナ'),
                        last_name_kana=self.data.get('last_name_kana', u'カナ'),
                        zip=self.data['zip'],
                        prefecture=self.data['prefecture'],
                        city=self.data['city'],
                        address_1=self.data['address_1'],
                        address_2=self.data['address_2'],
                        country=self.data['country'] if request.organization.setting.i18n else None,
                        email_1=self.data['email_1'],
                        tel_1=self.data['tel_1'],
                        tel_2=self.data['tel_2'],
                        fax=self.data['fax'],
                        sex=self.data['sex']
                        )


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

            def validate(self):
                # このように and 演算子を展開しないとすべてが一度に評価されない
                status = super(ClientForm, self).validate()
                status = self._validate_email_addresses() and status
                return status
        return ClientForm

    def make_show_lotentry_form(self):
        _ = self._
        class ShowLotEntryForm(OurForm):
            def _get_translations(self):
                return Translations()

            entry_no = fields.TextField(_(u"抽選申し込み番号"), validators=[v.Required(_(u'入力してください'))])
            tel_no = fields.TextField(_(u"電話番号"), validators=[v.Required(_(u'入力してください'))])
        return ShowLotEntryForm
