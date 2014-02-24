# -*- coding: utf-8 -*-

from altair.formhelpers.form import OurForm
from wtforms.fields import PasswordField, HiddenField, FormField
from altair.formhelpers import filters
from altair.formhelpers.widgets import OurTextInput
from altair.formhelpers.fields import OurTextField, OurIntegerField, OurSelectField, OurBooleanField, OurDecimalField
from wtforms.validators import Length, Regexp, Email, Optional

from altair.formhelpers import Translations, Required, Phone
from altair.app.ticketing.master.models import Prefecture
from altair.app.ticketing.core import models as c_models
from altair.app.ticketing.users import models as u_models
from altair.app.ticketing.login.main.forms import OperatorForm
from altair.saannotation import get_annotations_for

class OrganizationForm(OurForm):

    def _get_translations(self):
        return Translations()

    name = OurTextField(
        label=u'取引先名',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    code = OurTextField(
        label = u'組織コード',
        validators=[
            Required(),
            Regexp(u'^[A-Z0-9]*$', message=u'数字およびアルファベット大文字のみ入力できます'),
            Length(min=2, max=2, message=u'2文字で入力してください'),
        ]
    )
    short_name = OurTextField(
        label = u'短縮名',
        validators=[
            Required(),
            Regexp(u'^[a-zA-Z0-9_-]*$', message=u'半角英数字のみ入力できます'),
            Length(max=32, message=u'32文字以内で入力してください'),
        ]
    )
    client_type = OurSelectField(
        label=u'取引先タイプ',
        choices=[(1, u'スタンダード')],
        coerce=int,
    )
    contact_email = OurTextField(
        label = u'問い合わせメールアドレス',
        validators=[
            Required(),
            Email(),
        ]
    )
    company_name = OurTextField(
        label=u'会社名',
        validators=[Optional()]
    )
    section_name = OurTextField(
        label=u'部署名',
        validators=[Optional()]
    )
    zip = OurTextField(
        label=u'郵便番号',
        validators=[Optional()]
    )
    prefecture_id = OurSelectField(
        label=u'都道府県',
        validators=[Optional()],
        choices=[(pref.name, pref.name) for pref in Prefecture.all()]
    )
    city = OurTextField(
        label=u'市区町村',
        validators=[
            Optional(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    address_1 = OurTextField(
        label=u'町名以下の住所',
        validators=[
            Optional(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    address_2 = OurTextField(
        label=u'建物名など',
        validators=[
            Optional(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    tel_1 = OurTextField(
        label=u'電話番号',
        validators=[Phone()]
    )
    tel_2 = OurTextField(
        label=u'携帯電話番号',
        validators=[Phone()]
    )
    fax = OurTextField(
        label=u'FAX番号',
        validators=[Phone()]
    )

class NewOrganizationForm(OrganizationForm):
    login = FormField(form_class=OperatorForm)

class SejTenantForm(OurForm):
    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        super(SejTenantForm, self).__init__(formdata, obj, prefix, **kwargs)
        if 'organization_id' in kwargs:
            self.organization_id.data = kwargs['organization_id']

    def _get_translations(self):
        return Translations()

    organization_id = HiddenField(
        label='',
        validators=[Optional()],
    )
    id = HiddenField(
        label=u'ID',
        validators=[Optional()],
    )
    shop_id = OurTextField(
        label=u'ショップID',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    shop_name = OurTextField(
        label=u'ショップ名',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    contact_01 = OurTextField(
        label=u'連絡先1',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    contact_02 = OurTextField(
        label=u'連絡先2',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    api_key = OurTextField(
        label=u'API KEY',
        validators=[
            Optional(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ],
        filters=[
            filters.strip_spaces,
            lambda x: None if not x else x,
            ]
    )
    inticket_api_url = OurTextField(
        label=u'API URL',
        validators=[
            Optional(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ],
        filters=[
            filters.strip_spaces,
            lambda x: None if not x else x,
            ]
    )

def encoder(x):
    return x or u''

class OrganizationSettingForm(OurForm):
    id = HiddenField(
        label=u'ID',
        validators=[Optional()],
    )

    name = OurTextField(
        label=get_annotations_for(c_models.OrganizationSetting.name)['label'],
        validators=[
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
        )
    auth_type = OurSelectField(
        label=get_annotations_for(c_models.OrganizationSetting.auth_type)['label'],
        coerce=lambda x: x or None,
        encoder=lambda x: x or u'',
        choices=[
            (u'', u'未設定'),
            (u'fc_auth', u'FC会員ログイン'),
            (u'rakuten', u'楽天会員認証'),
            ]
        )
    performance_selector = OurSelectField(
        label=get_annotations_for(c_models.OrganizationSetting.performance_selector)['label'],
        choices=[
            (u'matchup', u'公演名でグルーピング'),
            (u'date', u'日付でグルーピング'),
            ]
        )
    margin_ratio = OurDecimalField(
        label=get_annotations_for(c_models.OrganizationSetting.margin_ratio)['label'],
        validators=[Optional()]
        )
    refund_ratio = OurDecimalField(
        label=get_annotations_for(c_models.OrganizationSetting.refund_ratio)['label'],
        validators=[Optional()]
        )
    printing_fee = OurDecimalField(
        label=get_annotations_for(c_models.OrganizationSetting.printing_fee)['label'],
        validators=[Optional()]
        )
    registration_fee = OurDecimalField(
        label=get_annotations_for(c_models.OrganizationSetting.registration_fee)['label'],
        validators=[Optional()]
        )
    multicheckout_shop_name = OurTextField(
        label=get_annotations_for(c_models.OrganizationSetting.multicheckout_shop_name)['label']
        )
    multicheckout_shop_id = OurTextField(
        label=get_annotations_for(c_models.OrganizationSetting.multicheckout_shop_id)['label']
        )
    multicheckout_auth_id = OurTextField(
        label=get_annotations_for(c_models.OrganizationSetting.multicheckout_auth_id)['label']
        )
    multicheckout_auth_password = PasswordField(
        label=get_annotations_for(c_models.OrganizationSetting.multicheckout_auth_password)['label']
        )
    cart_item_name = OurTextField(
        label=get_annotations_for(c_models.OrganizationSetting.cart_item_name)['label']
        )
    contact_pc_url = OurTextField(
        label=get_annotations_for(c_models.OrganizationSetting.contact_pc_url)['label']
        )
    contact_mobile_url = OurTextField(
        label=get_annotations_for(c_models.OrganizationSetting.contact_mobile_url)['label']
        )
    point_type = OurSelectField(
        label=get_annotations_for(c_models.OrganizationSetting.point_type)['label'],
        coerce=lambda x: int(x) if x else None,
        choices=[(0, u'無効')] + [(int(e.v), e.k) for e in u_models.UserPointAccountTypeEnum._values]
        )
    point_fixed = OurDecimalField(
        label=get_annotations_for(c_models.OrganizationSetting.point_fixed)['label'],
        validators=[Optional()]
        )
    point_rate = OurDecimalField(
        label=get_annotations_for(c_models.OrganizationSetting.point_rate)['label'],
        validators=[Optional()]
        )
    notify_point_granting_failure = OurBooleanField(
        label=get_annotations_for(c_models.OrganizationSetting.notify_point_granting_failure)['label']
        )
    bcc_recipient = OurTextField(
        label=get_annotations_for(c_models.OrganizationSetting.bcc_recipient)['label']
        )
    entrust_separate_seats = OurBooleanField(
        label=get_annotations_for(c_models.OrganizationSetting.entrust_separate_seats)['label']
        )
    augus_use = OurBooleanField(
        label=get_annotations_for(c_models.OrganizationSetting.augus_use)['label']
        )
    augus_customer_id = OurTextField(
        label=get_annotations_for(c_models.OrganizationSetting.augus_customer_id)['label']
        )
    augus_upload_url = OurTextField(
        label=get_annotations_for(c_models.OrganizationSetting.augus_upload_url)['label']
        )
    augus_download_url = OurTextField(
        label=get_annotations_for(c_models.OrganizationSetting.augus_download_url)['label']
        )
    augus_username = OurTextField(
        label=get_annotations_for(c_models.OrganizationSetting.augus_username)['label']
        )
    augus_password = OurTextField(
        label=get_annotations_for(c_models.OrganizationSetting.augus_password)['label']
        )


class HostForm(OurForm):
    host_name = OurTextField(
        label=get_annotations_for(c_models.Host.host_name)['label'],
        validators=[Required()]
        )
    path = OurTextField(
        label=get_annotations_for(c_models.Host.path)['label']
        )
    base_url = OurTextField(
        label=get_annotations_for(c_models.Host.base_url)['label']
        )
    mobile_base_url = OurTextField(
        label=get_annotations_for(c_models.Host.mobile_base_url)['label']
        )
