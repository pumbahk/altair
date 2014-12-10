# encoding: utf-8

from pyramid.i18n import TranslationString as _
from wtforms.validators import Length, Optional
from altair.app.ticketing.helpers import label_text_for
from altair.formhelpers.form import OurForm
from altair.formhelpers.filters import (
    replace_ambiguous,
    zero_as_none,
    blank_as_none,
    )
from altair.formhelpers.validators import (
    Required,
    JISX0208,
    after1900,
    DynSwitchDisabled,
    )
from altair.formhelpers.translations import Translations
from altair.formhelpers.fields import (
    OurSelectField,
    OurSelectMultipleDictField,
    OurTextField,
    JSONField,
    )
from altair.formhelpers.fields.select import WTFormsChoicesWrapper
from altair.formhelpers.widgets import (
    CheckboxMultipleSelect,
    OurTextArea,
    )
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.cart.models import CartSetting
from altair.app.ticketing.master.models import Prefecture
from altair.app.ticketing.events.sales_segments.forms import ExtraFormEditorWidget

from . import cart_setting_types

class PrefectureSelectModel(object):
    def __init__(self, prefectures):
        self.prefectures = prefectures

    def encoder(self, v):
        return unicode(v) if v is not None else u''

    def decoder(self, v):
        return unicode(v) if v else None

    def items(self):
        yield u'', None, _(u'未設定')
        for prefecture in self.prefectures:
            yield prefecture.name, prefecture.name, prefecture.name

    def __len__(self):
        return len(self.prefectures)

    def __contains__(self, v):
        decoded_value = self.decoder(v)
        if decoded_value is None:
            return True
        for prefecture in self.prefectures:
            if prefecture.name == decoded_value:
                return True
        else:
            return False

    def __iter__(self):
        for prefecture in self.prefectures:
            yield prefecture.id


class CartSettingForm(OurForm):
    def _get_translation(self):
        return Translations()

    name = OurTextField(
        label=label_text_for(CartSetting.name),
        validators=[Required()],
        filters=[blank_as_none]
        )

    def _cart_setting_types(field):
        retval = list(cart_setting_types)
        keys = set(k for k, _ in cart_setting_types)
        for (k, ) in DBSession.query(CartSetting.type).filter_by(organization_id=field._form.context.organization.id).distinct():
            if k not in keys:
                retval.append((k, k))
        return retval

    type = OurSelectField(
        label=label_text_for(CartSetting.type),
        validators=[Optional()],
        choices=_cart_setting_types
        )

    title = OurTextField(
        label=_(u'カートのタイトル')
        )

    contact_url = OurTextField(
        label=_(u'お問い合わせ先URL')
        )

    contact_url_mobile = OurTextField(
        label=_(u'お問い合わせ先URL (携帯)')
        )

    contact_tel = OurTextField(
        label=_(u'お問い合わせ先電話番号')
        )

    contact_office_hours = OurTextField(
        label=_(u'お問い合わせ先営業時間')
        )

    contact_name = OurTextField(
        label=_(u'お問い合わせ先の名称')
        )

    privacy_policy_page_url = OurTextField(
        label=_(u'プライバシーポリシーページのURL (PC / スマートフォン)')
        )

    privacy_policy_page_url_mobile = OurTextField(
        label=_(u'プライバシーポリシーページのURL (携帯)')
        )

    legal_notice_page_url = OurTextField(
        label=_(u'「特商法に基づく表示」ページのURL (PC / スマートフォン)')
        )

    legal_notice_page_url_mobile = OurTextField(
        label=_(u'「特商法に基づく表示」ページのURL (携帯)')
        )

    mail_filter_domain_notice_template = OurTextField(
        label=_(u'メールフィルターの設定確認文言'),
        widget=OurTextArea()
        )

    orderreview_page_url = OurTextField(
        label=_(u'購入履歴確認ページのURL')
        )

    mobile_marker_color = OurTextField(
        label=_(u'携帯向けカートの見出しにつく「■」の色')
        )

    mobile_required_marker_color = OurTextField(
        label=_(u'携帯向けカートの必須項目名の横につく「*」の色')
        )

    mobile_header_background_color = OurTextField(
        label=_(u'携帯向けカートのヘッダの背景色')
        )

    performance_selector = OurSelectField(
        label=label_text_for(CartSetting.performance_selector),
        validators=[
            DynSwitchDisabled('{type} = "fc"')
            ],
        model=WTFormsChoicesWrapper([
            (u'', u'未設定 (デフォルトの設定に従う)'),
            (u'matchup', u'公演名でグルーピング'),
            (u'date', u'日付でグルーピング'),
            ],
            coerce_getter=lambda:lambda v: v if v != u'' else None,
            encoder_getter=lambda:lambda v: unicode(v) if v is not None else u''
            )
        )

    performance_selector_label1_override = OurTextField(
        label=label_text_for(CartSetting.performance_selector_label1_override),
        filters=[
            replace_ambiguous,
            blank_as_none,
            ],
        validators=[
            DynSwitchDisabled('{type} = "fc"'),
            JISX0208,
            Length(max=100),
            ]
        )
    performance_selector_label2_override = OurTextField(
        label=label_text_for(CartSetting.performance_selector_label2_override),
        filters=[
            replace_ambiguous,
            blank_as_none,
            ],
        validators=[
            DynSwitchDisabled('{type} = "fc"'),
            JISX0208,
            Length(max=100),
            ]
        )

    default_prefecture = OurSelectField(
        label=_(u'デフォルトの都道府県'),
        model=PrefectureSelectModel(Prefecture.all())
        )

    flavors = OurSelectMultipleDictField(
        label=_(u'お好み設定'),
        choices=[
            (u'japanese_prefectures', _(u'日本の都道府県名を強制する')),
            (u'mobile_and_landline_phone_number', _(u'固定電話と携帯電話番号の両方を入力させる')),
            (u'pc_and_mobile_email_address', _(u'PCメールアドレスと携帯メールアドレスの両方を入力させる')),
            ],
        widget=CheckboxMultipleSelect(multiple=True)
        )

    extra_form_fields = JSONField(
        label=u'追加フィールド',
        filters=[blank_as_none],
        validators=[
            DynSwitchDisabled('{type} <> "fc"')
            ],
        widget=ExtraFormEditorWidget()
        )

    header_image_url = OurTextField(
        label=_(u'ヘッダ画像のURL (PC)')
        )

    header_image_url_mobile = OurTextField(
        label=_(u'ヘッダ画像のURL (モバイル)')
        )

    def __init__(self, *args, **kwargs):
        self.context = kwargs.pop('context', None)
        super(CartSettingForm, self).__init__(*args, **kwargs)
