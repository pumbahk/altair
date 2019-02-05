# -*- coding: utf-8 -*-

from pyramid.i18n import TranslationString as _
from altair.formhelpers.form import OurForm
from wtforms.fields import PasswordField, HiddenField, FormField
from altair.formhelpers import filters
from altair.formhelpers.widgets import OurTextInput, CheckboxMultipleSelect
from altair.formhelpers.fields import (
    OurTextField,
    OurIntegerField,
    OurSelectField,
    OurBooleanField,
    OurDecimalField,
    DelimitedTextsField,
    OurSelectMultipleField
)
from altair.formhelpers.validators import DynSwitchDisabled
from wtforms.validators import Length, Regexp, Optional, ValidationError
from wtforms.compat import iteritems
from wtforms.form import WebobInputWrapper

from altair.formhelpers import Translations, Required, Phone, Email
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.master.models import Prefecture
from altair.app.ticketing.core import models as c_models
from altair.app.ticketing.users import models as u_models
from altair.app.ticketing.cart import models as cart_models
from altair.app.ticketing.login.main.forms import OperatorForm
from altair.saannotation import get_annotations_for
from altair.app.ticketing.core.models import Organization, OrganizationSetting
from altair.app.ticketing.operators.models import OperatorAuth, ensure_ascii


class OrganizationFormMixin(object):

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
        label = u'問い合わせメールアドレス (TSから見た)',
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
        coerce=int,
        validators=[Optional()],
        choices=[(pref.id, pref.name) for pref in Prefecture.all()]
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
        label=u'電話番号1',
        validators=[Phone()]
    )
    tel_2 = OurTextField(
        label=u'電話番号2',
        validators=[Phone()]
    )
    fax = OurTextField(
        label=u'FAX番号',
        validators=[Phone()]
    )


class NewOrganizationOperatorForm(OperatorForm):
    def validate_login_id(self, field):
        operator_auth = OperatorAuth.get_by_login_id(ensure_ascii(field.data))
        if operator_auth is not None:
            raise ValidationError(u'ログインIDが重複しています。')
        return True


class OrganizationForm(OurForm, OrganizationFormMixin):
    """Organization更新時
    """
    def __init__(self, *args, **kwds):
        self._organization_id = kwds.get('organization_id', None)
        super(OrganizationForm, self).__init__(*args, **kwds)

    def _get_organization_id(self):
        try:
            return int(self._organization_id)
        except (TypeError, ValueError):
            return None

    def validate_code(self, field):
        """自分自身以外に同じcodeが登録されていないか確認する
        """
        organization_id = self._get_organization_id()
        if organization_id is None:
            raise ValidationError(u'オーガ二ゼーションIDが不正です')

        duplicate_organizations = c_models.Organization \
            .query \
            .filter(c_models.Organization.id != organization_id) \
            .filter(c_models.Organization.code == field.data) \
            .all()

        if duplicate_organizations:
            raise ValidationError(u'既に同じ短縮コードの取引先名が登録されています')
        return True

    def validate_short_name(self, field):
        """自分自身以外に同じshort_nameが登録されていないか確認する
        """
        organization_id = self._get_organization_id()
        if organization_id is None:
            raise ValidationError(u'オーガ二ゼーションIDが不正です')

        duplicate_organizations = c_models.Organization \
            .query \
            .filter(c_models.Organization.id != organization_id) \
            .filter(c_models.Organization.short_name == field.data) \
            .all()

        if duplicate_organizations:
            raise ValidationError(u'既に同じ短縮名の取引先名が登録されています')
        return True


class NewOrganizationForm(OurForm, OrganizationFormMixin):
    """Organization新規作成時
    """

    login = FormField(form_class=NewOrganizationOperatorForm)

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        if 'request' in kwargs:
            self.request = kwargs['request']
        super(NewOrganizationForm, self).__init__(formdata, obj, prefix, **kwargs)

    default_mail_sender = OurTextField(
        label=get_annotations_for(c_models.OrganizationSetting.default_mail_sender)['label']
        )

    def validate_name(self, field):
        query = c_models.Organization.filter_by(name=field.data)
        if query is None:
            return
        org = query.first()
        if org is not None:
            raise ValidationError(u'既に同名の取引先名が登録されています')
        return True

    def validate_code(self, field):
        query = c_models.Organization.filter_by(code=field.data)
        if query is None:
            return
        org = query.first()
        if org is not None:
            raise ValidationError(u'既に同じ短縮コードの取引先名が登録されています')
        return True

    def validate_short_name(self, field):
        query = c_models.Organization.filter_by(short_name=field.data)
        if query is None:
            return
        org = query.first()
        if org is not None:
            raise ValidationError(u'既に同じ短縮名の取引先名が登録されています')
        return True


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
        label=u'電話番号',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
            Regexp(r'^[-\d]*$', message=u'半角数字および-(ハイフン)のみを入力してください'),
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

class OrganizationSettingSimpleForm(OurForm):
    id = HiddenField(
        label=u'ID',
        validators=[Optional()],
    )

    notify_remind_mail = OurBooleanField(
        label=get_annotations_for(c_models.OrganizationSetting.notify_remind_mail)['label']
        )

    notify_print_remind_mail = OurBooleanField(
        label=get_annotations_for(c_models.OrganizationSetting.notify_print_remind_mail)['label']
        )

    contact_pc_url = OurTextField(
        label=get_annotations_for(c_models.OrganizationSetting.contact_pc_url)['label']
        )
    contact_mobile_url = OurTextField(
        label=get_annotations_for(c_models.OrganizationSetting.contact_mobile_url)['label']
        )
    point_type = OurSelectField(
        label=get_annotations_for(c_models.OrganizationSetting.point_type)['label'],
        validators=[Optional()],
        coerce=lambda x: int(x) if x else None,
        choices=[(0, u'無効')] + [(int(e.v), e.k) for e in u_models.UserPointAccountTypeEnum._values]
        )
    point_fixed = OurDecimalField(
        label=get_annotations_for(c_models.OrganizationSetting.point_fixed)['label'],
        validators=[
            Optional(),
            DynSwitchDisabled('{point_type} = 0'),
            ]
        )
    point_rate = OurDecimalField(
        label=get_annotations_for(c_models.OrganizationSetting.point_rate)['label'],
        validators=[
            Optional(),
            DynSwitchDisabled('{point_type} = 0'),
            ]
        )
    notify_point_granting_failure = OurBooleanField(
        label=get_annotations_for(c_models.OrganizationSetting.notify_point_granting_failure)['label']
        )
    entrust_separate_seats = OurBooleanField(
        label=get_annotations_for(c_models.OrganizationSetting.entrust_separate_seats)['label']
        )
    bcc_recipient = OurTextField(
        label=get_annotations_for(c_models.OrganizationSetting.bcc_recipient)['label']
        )
    default_mail_sender = OurTextField(
        label=get_annotations_for(c_models.OrganizationSetting.default_mail_sender)['label']
        )
    sales_report_type = OurSelectField(
        label=get_annotations_for(c_models.OrganizationSetting.sales_report_type)['label'],
        coerce=lambda x: int(x) if x else None,
        choices=[(int(e.v), e.k) for e in c_models.SalesReportTypeEnum]
        )
    cart_setting_id = OurSelectField(
        label=get_annotations_for(c_models.OrganizationSetting.cart_setting_id)['label'],
        # これは現在編集中の Organization の cart_setting であるべきなので context.organization.id を使ってはいけない (TKT-966)
        choices=lambda field: [(str(cart_setting.id), (cart_setting.name or u'(名称なし)')) for cart_setting in DBSession.query(cart_models.CartSetting).filter_by(organization_id=field._form.organization.id)],
        coerce=int
        )
    mail_refund_to_user = OurBooleanField(
        label=get_annotations_for(c_models.OrganizationSetting.mail_refund_to_user)['label']
    )
    lot_entry_user_withdraw = OurBooleanField(
        label=get_annotations_for(c_models.OrganizationSetting.lot_entry_user_withdraw)['label']
    )
    lot_entry_lock = OurBooleanField(
        label=get_annotations_for(c_models.OrganizationSetting.lot_entry_lock)['label']
    )
    auto_cms = OurBooleanField(
        label=get_annotations_for(c_models.OrganizationSetting.auto_cms)['label']
    )
    recaptcha = OurBooleanField(
        label=get_annotations_for(c_models.OrganizationSetting.recaptcha)['label']
    )
    tapirs = OurBooleanField(
        label=get_annotations_for(c_models.OrganizationSetting.tapirs)['label']
    )
    i18n = OurBooleanField(
        label=get_annotations_for(c_models.OrganizationSetting.i18n)['label']
    )
    default_locale = OurSelectField(
        label=_(u'デフォルト言語'),
        validators=[Optional()],
        choices=[(k, getattr(c_models.OrganizationSettingDefaultLocaleEnum, k).v) for k in
                 c_models.OrganizationSettingDefaultLocaleEnum.order.v],
    )

    def __init__(self, *args, **kwargs):
        context = kwargs.pop('context')
        organization = kwargs.pop('organization')
        super(OrganizationSettingSimpleForm, self).__init__(*args, **kwargs)
        self.context = context
        self.organization = organization


class OrganizationSettingForm(OrganizationSettingSimpleForm):
    name = OurTextField(
        label=get_annotations_for(c_models.OrganizationSetting.name)['label'],
        validators=[
            Length(max=255, message=u'255文字以内で入力してください'),
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
    point_type = OurSelectField(
        label=get_annotations_for(c_models.OrganizationSetting.point_type)['label'],
        coerce=lambda x: int(x) if x else None,
        choices=[(0, u'無効')] + [(int(e.v), e.k) for e in u_models.UserPointAccountTypeEnum._values]
        )
    point_group_id = OurIntegerField(
        label=get_annotations_for(c_models.OrganizationSetting.point_group_id)['label'],
        validators=[
            DynSwitchDisabled('{enable_point_allocation} = 0'),
            ]
        )
    point_reason_id = OurIntegerField(
        label=get_annotations_for(c_models.OrganizationSetting.point_reason_id)['label'],
        validators=[
            DynSwitchDisabled('{enable_point_allocation} = 0'),
            ]
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
    enable_smartphone_cart = OurBooleanField(
        label=get_annotations_for(c_models.OrganizationSetting.enable_smartphone_cart)['label']
        )
    enable_mypage = OurBooleanField(
        label=get_annotations_for(c_models.OrganizationSetting.enable_mypage)['label']
    )
    recaptcha = OurBooleanField(
        label=get_annotations_for(c_models.OrganizationSetting.recaptcha)['label']
    )
    tapirs = OurBooleanField(
        label=get_annotations_for(c_models.OrganizationSetting.tapirs)['label']
    )
    enable_discount_code = OurBooleanField(
        label=get_annotations_for(c_models.OrganizationSetting.enable_discount_code)['label']
    )
    enable_resale = OurBooleanField(
        label=get_annotations_for(c_models.OrganizationSetting.enable_resale)['label']
    )
    enable_price_batch_update = OurBooleanField(
        label=get_annotations_for(c_models.OrganizationSetting.enable_price_batch_update)['label']
    )
    enable_passport = OurBooleanField(
        label=get_annotations_for(c_models.OrganizationSetting.enable_passport)['label']
    )
    enable_point_allocation = OurBooleanField(
        label=get_annotations_for(c_models.OrganizationSetting.enable_point_allocation)['label']
    )
    enable_word = OurBooleanField(
        label=get_annotations_for(c_models.OrganizationSetting.enable_word)['label']
    )
    augus_use = OurBooleanField(
        label=get_annotations_for(c_models.OrganizationSetting.augus_use)['label']
        )
    asid = OurTextField(
        label=get_annotations_for(c_models.OrganizationSetting.asid)['label']
        )
    asid_mobile = OurTextField(
        label=get_annotations_for(c_models.OrganizationSetting.asid_mobile)['label']
        )
    asid_smartphone = OurTextField(
        label=get_annotations_for(c_models.OrganizationSetting.asid_smartphone)['label']
        )
    lot_asid = OurTextField(
        label=get_annotations_for(c_models.OrganizationSetting.lot_asid)['label']
        )
    lot_entry_lock = OurBooleanField(
        label=get_annotations_for(c_models.OrganizationSetting.lot_entry_lock)['label']
    )
    sitecatalyst_use = OurBooleanField(
        label=get_annotations_for(c_models.OrganizationSetting.sitecatalyst_use)['label']
        )
    famiport_enabled = OurBooleanField(
        label=get_annotations_for(c_models.OrganizationSetting.famiport_enabled)['label']
        )
    enable_fm_reflection_func = OurBooleanField(
        label=get_annotations_for(c_models.OrganizationSetting.enable_fm_reflection_func)['label']
        )
    orderreview_index = OurSelectField(
        label=get_annotations_for(c_models.OrganizationSetting.orderreview_index)['label'],
        coerce=lambda x: int(x) if x else None,
        choices=[e.v for e in c_models.OrderreviewIndexEnum],
        validators=[]
        )
    i18n = OurBooleanField(
        label=get_annotations_for(c_models.OrganizationSetting.i18n)['label']
        )
    default_locale = OurSelectField(
        label=_(u'デフォルト言語'),
        validators=[Optional()],
        choices=[(k, getattr(c_models.OrganizationSettingDefaultLocaleEnum, k).v) for k in
                 c_models.OrganizationSettingDefaultLocaleEnum.order.v],
    )
    auto_cms = OurBooleanField(
        label=get_annotations_for(c_models.OrganizationSetting.auto_cms)['label']
    )
    event_label = OurBooleanField(
        label=get_annotations_for(c_models.OrganizationSetting.event_label)['label']
    )
    show_event_op_and_sales = OurBooleanField(
        label=get_annotations_for(c_models.OrganizationSetting.show_event_op_and_sales)['label']
    )
    oauth_client_id = OurTextField(
        label=_(u'OAuthクライアントID')
        )

    oauth_client_secret = OurTextField(
        label=_(u'OAuthクライアントシークレット')
        )

    oauth_endpoint_authz = OurTextField(
        label=_(u'OAuth認可エンドポイント')
        )

    oauth_endpoint_token = OurTextField(
        label=_(u'OAuthトークン発行エンドポイント')
        )

    oauth_endpoint_token_revocation = OurTextField(
        label=_(u'OAuthトークン無効化エンドポイント')
        )

    oauth_endpoint_api = OurTextField(
        label=_(u'OAuthAPIエンドポイント')
        )

    oauth_scope = DelimitedTextsField(
        label=_(u'OAuthスコープ (スペース区切り)'),
        delimiter_pattern=ur'\s+',
        canonical_delimiter=u' ',
        widget=OurTextInput()
        )

    openid_prompt = OurSelectMultipleField(
        label=_(u'OpenID Connectのログインプロンプト設定'),
        choices=[
            (u'none', u'一切のユーザーへのプロンプトを許可しない'),
            (u'login', u'すでにOPで認証済みでもログイン画面を出す'),
            (u'select_account', u'アカウントの選択を要求'),
            ],
        widget=CheckboxMultipleSelect(multiple=True)
        )

    oauth_service_provider = OurSelectField(
        label=_(u'認証サービスプロバイダ(OAuth使用時のみ指定)'),
        choices=[
            (u'', u'なし'),
            (u'rakuten', u'楽天認証'),
            (u'pollux', u'ファンクラブ認証(pollux)'),
            ]
        )

    rendered_template_1 = OurSelectField(
        label=get_annotations_for(c_models.OrganizationSetting.rendered_template_1)['label'],
        choices=lambda field: [(org.short_name, u'{}: {}'.format(org.short_name, org.name)) for org in
                               Organization.query.order_by(Organization.short_name).all()],
        coerce=str
        )

    rendered_template_2 = OurSelectField(
        label=get_annotations_for(c_models.OrganizationSetting.rendered_template_2)['label'],
        choices=[
            (u'__base__', u'__base__（HTML5）'),
            (u'__default__', u'__default__（XHTML）'),
            (u'-', u'利用しない'),
            ],
        coerce=str,
        )

    enable_agreement_of_policy = OurBooleanField(
        label=get_annotations_for(c_models.OrganizationSetting.enable_agreement_of_policy)['label']
    )
    enable_spa_cart = OurBooleanField(
        label=get_annotations_for(c_models.OrganizationSetting.enable_spa_cart)['label']
    )

    def validate_multicheckout_shop_name(form, field):
        org_setting = OrganizationSetting.query.\
            filter(OrganizationSetting.multicheckout_shop_name==field.data).\
            filter(OrganizationSetting.id!=form.id.data).all()
        if org_setting:
            raise ValueError(u'既に同じ名前の店舗名称があります。')

    def validate_cart_item_name(self, field):
        if len(field.data.encode('shift_jis')) > 36:
            raise ValueError(u'登録可能な文字数を超えています。36byte以内(全角18文字分、半角36文字分)で入力してください。')

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
