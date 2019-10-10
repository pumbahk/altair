# -*- coding: utf-8 -*-

from wtforms.validators import Length, Optional
from markupsafe import Markup

from altair.formhelpers.form import OurForm
from altair.formhelpers.fields import OurTextField, OurSelectField, OurDecimalField, OurHiddenField
from altair.formhelpers.widgets import OurTextArea
from altair.formhelpers import Translations, Required, OurBooleanField
from altair.formhelpers.validators import DynSwitchDisabled, ValidationError
from altair.app.ticketing.core.models import DeliveryMethod, DeliveryMethodPlugin, OrganizationSetting
from altair.saannotation import get_annotations_for
from altair.app.ticketing.payments.plugins import SEJ_DELIVERY_PLUGIN_ID, QR_DELIVERY_PLUGIN_ID, \
    FAMIPORT_DELIVERY_PLUGIN_ID, RESERVE_NUMBER_DELIVERY_PLUGIN_ID, QR_AES_DELIVERY_PLUGIN_ID,\
    WEB_COUPON_DELIVERY_PLUGIN_ID, SKIDATA_QR_DELIVERY_PLUGIN_ID
def get_msg(target):
    msg = u'手数料は「予約ごと」または「{}」どちらか一方を入力してください。<br/>'
    msg += u'取得しない手数料は「0」を入力してください。'
    msg = Markup(msg.format(target))
    return msg


def get_dmp(organization_id):
    plugins_to_be_filtered = [QR_AES_DELIVERY_PLUGIN_ID, WEB_COUPON_DELIVERY_PLUGIN_ID]
    enable_skidata = OrganizationSetting.query.filter(OrganizationSetting.organization_id == organization_id) \
        .with_entities(OrganizationSetting.enable_skidata).scalar()
    if not enable_skidata:
        plugins_to_be_filtered.append(SKIDATA_QR_DELIVERY_PLUGIN_ID)
    return [(dmp.id, dmp.name) for dmp in DeliveryMethodPlugin.all() if dmp.id not in plugins_to_be_filtered]


class DeliveryMethodForm(OurForm):
    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        OurForm.__init__(self, formdata, obj, prefix, **kwargs)
        self.delivery_plugin_id.choices = get_dmp(getattr(self.organization_id, 'data', None))

    def _get_translations(self):
        return Translations()

    id = OurHiddenField(
        label=get_annotations_for(DeliveryMethod.id)['label'],
        validators=[Optional()]
        )
    organization_id = OurHiddenField(
        label=get_annotations_for(DeliveryMethod.organization_id)['label'],
        validators=[Optional()]
        )
    name = OurTextField(
        label=get_annotations_for(DeliveryMethod.name)['label'],
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
            ]
        )
    fee_per_order = OurDecimalField(
        label=get_annotations_for(DeliveryMethod.fee_per_order)['label'],
        places=0,
        validators=[Required()]
        )
    fee_per_principal_ticket = OurDecimalField(
        label=get_annotations_for(DeliveryMethod.fee_per_principal_ticket)['label'],
        places=0,
        validators=[Required()]
        )
    fee_per_subticket = OurDecimalField(
        label=get_annotations_for(DeliveryMethod.fee_per_subticket)['label'],
        places=0,
        validators=[Required()]
        )
    delivery_plugin_id = OurSelectField(
        label=get_annotations_for(DeliveryMethod.delivery_plugin_id)['label'],
        validators=[Required(u'選択してください')],
        choices=[],
        coerce=int
        )
    description = OurTextField(
        label=get_annotations_for(DeliveryMethod.description)['label'],
        widget=OurTextArea()
        )
    name_en = OurTextField(
        label=u'引取方法名(英語)',
        validators=[
            Length(max=255, message=u'255文字以内で入力してください'),
            ]
        )
    description_en = OurTextField(
        label=u"説明文(HTML)(英語)",
        widget=OurTextArea()
        )
    name_zh_cn = OurTextField(
        label=u'引取方法名(簡体中国語)',
        validators=[
            Length(max=255, message=u'255文字以内で入力してください'),
            ]
        )
    description_zh_cn = OurTextField(
        label=u"説明文(HTML)(簡体中国語)",
        widget=OurTextArea()
        )
    name_zh_tw = OurTextField(
        label=u'引取方法名(繁体中国語)',
        validators=[
            Length(max=255, message=u'255文字以内で入力してください'),
            ]
        )
    description_zh_tw = OurTextField(
        label=u"説明文(HTML)(繁体中国語)",
        widget=OurTextArea()
        )
    name_ko = OurTextField(
        label=u'引取方法名(韓国語)',
        validators=[
            Length(max=255, message=u'255文字以内で入力してください'),
            ]
        )
    description_ko = OurTextField(
        label=u"説明文(HTML)(韓国語)",
        widget=OurTextArea()
        )
    hide_voucher = OurBooleanField(
        label=u'引換票を表示しない',
        validators=[
            DynSwitchDisabled('AND({delivery_plugin_id} <> "%d", {delivery_plugin_id} <> "%d")' % (SEJ_DELIVERY_PLUGIN_ID, FAMIPORT_DELIVERY_PLUGIN_ID))
            ]
        )
    single_qr_mode = OurBooleanField(
        label=u'単一QRモード (一括発券)',
        validators=[
            DynSwitchDisabled('AND({delivery_plugin_id} <> "%d", {delivery_plugin_id} <> "%d")' % (QR_DELIVERY_PLUGIN_ID, QR_AES_DELIVERY_PLUGIN_ID))
            ]
        )
    expiration_date = OurTextField(
        label=u'チケット有効期限 (相対)',
        validators=[
            DynSwitchDisabled('AND({delivery_plugin_id} <> "%d", {delivery_plugin_id} <> "%d")' % (RESERVE_NUMBER_DELIVERY_PLUGIN_ID, WEB_COUPON_DELIVERY_PLUGIN_ID))
            ]
        )
    term_sales = OurBooleanField(
        label=u'期間券',
        validators=[
            DynSwitchDisabled('AND({delivery_plugin_id} <> "%d", {delivery_plugin_id} <> "%d")' % (
                RESERVE_NUMBER_DELIVERY_PLUGIN_ID, WEB_COUPON_DELIVERY_PLUGIN_ID))
        ]
    )
    public = OurBooleanField(
        label=u'公開する'
        )
    display_order = OurTextField(
        label=u'表示順',
        default=0,
    )
    selectable = OurBooleanField(
        label=u'使用可否',
        default=True,
    )

    def validate_expiration_date(form, field):
        if field.data:
            if str(field.data).isdigit() == False:
                raise ValidationError(u'数字（正数）のみ、入力できます。')

    def validate_fee_per_order(form, field):
        if form.data['fee_per_principal_ticket'] or form.data['fee_per_subticket']:
            if form.data[field.name]:
                if form.data['fee_per_principal_ticket'] and form.data['fee_per_subticket']:
                    raise ValidationError(get_msg(u'チケットごと:主券・副券'))
                elif form.data['fee_per_principal_ticket']:
                    raise ValidationError(get_msg(u'チケットごと:主券'))
                elif form.data['fee_per_subticket']:
                    raise ValidationError(get_msg(u'チケットごと:・副券'))

    def validate_fee_per_principal_ticket(form, field):
        if form.data['fee_per_order'] and form.data[field.name]:
            raise ValidationError(get_msg(u'チケットごと:主券'))

    def validate_fee_per_subticket(form, field):
        if form.data['fee_per_order'] and form.data[field.name]:
            raise ValidationError(get_msg(u'チケットごと:副券'))

    # organizationによるカスタマイズフィールド名を取得メソッド
    def get_customized_fields(self):
        """
        :return: list
        """
        return []

class QRAESDeliveryMethodForm(DeliveryMethodForm):
    """
    追加のカスタマイズのフィルド名は必ず'qr_aes_'からの文字列で命名ください。
    """
    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        super(QRAESDeliveryMethodForm, self).__init__(formdata=formdata, obj=obj, prefix=prefix, **kwargs)
        self.delivery_plugin_id.choices = [(dmp.id, dmp.name) for dmp in DeliveryMethodPlugin.all()]

    def get_customized_fields(self):
        names = []
        for attr in dir(self):
            if attr.startswith('qr_aes_'):
                names.append(attr)
        return names