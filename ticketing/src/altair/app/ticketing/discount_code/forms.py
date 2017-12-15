# -*- coding: utf-8 -*-

from altair.app.ticketing.core.models import Event
from altair.formhelpers import Translations, DateTimeFormat
from altair.formhelpers.fields import OurDateTimeField, OurSelectField
from altair.formhelpers.validators import Required, SwitchOptional
from altair.saannotation import get_annotations_for
from wtforms import Form
from wtforms import TextField, HiddenField, SelectField, BooleanField, TextAreaField, IntegerField
from wtforms.validators import Length, Optional, ValidationError, NumberRange
from .models import CodeOrganizerEnum, DiscountCodeSetting, DiscountCodeCode, DiscountCodeTarget


class DiscountCodeSettingForm(Form):
    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata, obj, prefix, **kwargs)
        if 'organization_id' in kwargs:
            self.organization_id = kwargs['organization_id']

    def _get_translations(self):
        return Translations()

    def _check_prefix(self):
        """
        入力された4桁の接頭辞の妥当性を確認。
        新たに登録しようとしている組み合わせが存在しないことを確認する。
        :return: エラーメッセージ
        """

        # 既存の設定の編集時（Hiddenで渡されるIDの有無で判断）
        if len(self.id.data) != 0:
            query = DiscountCodeSetting.filter_by(
                id=self.id.data,
                organization_id=self.organization_id,
                first_digit=self.first_digit.data,
                following_2to4_digits=self.following_2to4_digits.data
            )
            cnt = int(query.count())
            limit = 1
            if cnt == limit:
                # 既存の設定の接頭辞を編集しなかった場合、ここでリターン
                return True

        # 新規に設定を登録する場合、あるいは編集時に別の接頭辞に変更する場合
        query = DiscountCodeSetting.filter_by(
            organization_id=self.organization_id,
            first_digit=self.first_digit.data,
            following_2to4_digits=self.following_2to4_digits.data
        )
        cnt = int(query.count())
        limit = 0
        if cnt > limit:
            raise ValidationError(u'すでに使用されている組み合わせです')

        return True

    def validate_first_digit(self, request):
        self._check_prefix()

    def validate_following_2to4_digits(self, request):
        self._check_prefix()

    id = HiddenField(
        label=u'ID',
        validators=[Optional()],
    )
    is_valid = BooleanField(
        label=get_annotations_for(DiscountCodeSetting.is_valid)['label'],
        default=False,
        validators=[Optional()],
    )
    name = TextField(
        label=get_annotations_for(DiscountCodeSetting.name)['label'],
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    issued_by = OurSelectField(
        label=get_annotations_for(DiscountCodeSetting.issued_by)['label'],
        default=CodeOrganizerEnum.own.v[1],
        validators=[Required()],
        choices=[code_organizer.v for code_organizer in CodeOrganizerEnum],
        coerce=str
    )
    first_digit = SelectField(
        label=get_annotations_for(DiscountCodeSetting.first_digit)['label'],
        validators=[Required()],
        choices=[
            ('T', u'T')
        ],
        coerce=str
    )
    following_2to4_digits = TextField(
        label=get_annotations_for(DiscountCodeSetting.following_2to4_digits)['label'],
        validators=[
            Length(min=3, max=3, message=u'半角英数3文字で入力してください'),
        ]
    )
    criterion = SelectField(
        label=get_annotations_for(DiscountCodeSetting.criterion)['label'],
        validators=[Required()],
        choices=[
            ('price', u'チケット価格')
        ],
        coerce=str
    )
    condition_price_amount = IntegerField(
        label=get_annotations_for(DiscountCodeSetting.condition_price_amount)['label'],
        validators=[
            NumberRange(min=0, max=99999999, message=u'8桁以内の半角数字で入力してください')
        ]
    )
    condition_price_more_or_less = SelectField(
        label=get_annotations_for(DiscountCodeSetting.condition_price_more_or_less)['label'],
        validators=[Required()],
        choices=[
            ('less', u'以下')
        ],
        coerce=str
    )
    benefit_amount = TextField(
        label=get_annotations_for(DiscountCodeSetting.benefit_amount)['label'],
        validators=[
            Required(),
            Length(max=8, message=u'8桁以内で入力してください'),
        ]
    )
    benefit_unit = SelectField(
        label=get_annotations_for(DiscountCodeSetting.benefit_unit)['label'],
        validators=[Required()],
        choices=[
            ('%', u'%')
        ],
        coerce=str
    )
    start_at = OurDateTimeField(
        label=get_annotations_for(DiscountCodeSetting.start_at)['label'],
        validators=[SwitchOptional('end_at'),
                    Required(),
                    DateTimeFormat()],
        format='%Y-%m-%d %H:%M',
    )
    end_at = OurDateTimeField(
        label=get_annotations_for(DiscountCodeSetting.end_at)['label'],
        validators=[SwitchOptional('start_at'),
                    Required(),
                    DateTimeFormat()],
        format='%Y-%m-%d %H:%M',
    )
    explanation = TextAreaField(
        label=get_annotations_for(DiscountCodeSetting.explanation)['label'],
        validators=[Optional()],
        default=u'''
概要:
適用条件：
割引内容：
        '''
    )
    status = HiddenField(
        label=u'状態',
    )


class DiscountCodeCodesForm(Form):
    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata, obj, prefix, **kwargs)
        if 'organization_id' in kwargs:
            self.organization_id = kwargs['organization_id']

    id = HiddenField(
        label=u'ID',
        validators=[Optional()],
    )
    discount_code_setting_id = HiddenField(
        label=get_annotations_for(DiscountCodeCode.discount_code_setting_id)['label'],
        validators=[Optional()],
    )
    organization_id = HiddenField(
        label=get_annotations_for(DiscountCodeCode.organization_id)['label'],
        validators=[Optional()],
    )
    operator_id = HiddenField(
        label=get_annotations_for(DiscountCodeCode.operator_id)['label'],
        validators=[Optional()],
    )
    code = TextField(
        label=get_annotations_for(DiscountCodeCode.code)['label'],
        validators=[
            Required(),
            Length(min=12, max=12, message=u'12桁で入力してください'),
        ]
    )
    order_no = TextField(
        label=get_annotations_for(DiscountCodeCode.order_no)['label'],
        validators=[Optional()],
    )
    used_at = OurDateTimeField(
        label=get_annotations_for(DiscountCodeCode.used_at)['label'],
        validators=[Optional(),
                    DateTimeFormat()],
        format='%Y-%m-%d %H:%M',
    )
    generate_num = TextField(
        label=u'コード生成数',
        validators=[Required()],
    )


class DiscountCodeTargetForm(Form):
    id = HiddenField(
        label=u'ID',
        validators=[Optional()],
    )
    discount_code_setting_id = HiddenField(
        label=get_annotations_for(DiscountCodeTarget.discount_code_setting_id)['label'],
        validators=[Optional()],
    )
    event_id = IntegerField(
        label=get_annotations_for(DiscountCodeTarget.event_id)['label'],
        default=False,
        validators=[Optional()],
    )
    performance_id = IntegerField(
        label=get_annotations_for(DiscountCodeTarget.performance_id)['label'],
        default=False,
        validators=[Optional()],
    )


class SearchTargetForm(Form):
    event_title = TextField(
        label=get_annotations_for(Event.title)['label'],
        validators=[Optional()],
    )
