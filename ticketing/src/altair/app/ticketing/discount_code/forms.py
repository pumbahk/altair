# -*- coding: utf-8 -*-

from altair.formhelpers import Translations, DateTimeFormat
from altair.formhelpers.fields import OurDateTimeField, OurSelectField
from altair.formhelpers.validators import Required, SwitchOptional
from altair.saannotation import get_annotations_for
from wtforms import Form
from wtforms import TextField, HiddenField, SelectField, BooleanField, TextAreaField
from wtforms.validators import Length, Optional, ValidationError
from .models import CodeOrganizerEnum, DiscountCodeSetting


class DiscountCodeSettingForm(Form):
    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata, obj, prefix, **kwargs)
        if 'organization_id' in kwargs:
            self.organization_id = kwargs['organization_id']

        # コード管理元が自社以外であれば、接頭辞は必須ではなくなる
        if self.issued_by.data != 'own':
            self.first_digit.validators = [Optional()]
            self.following_2to4_digits.validators = [Optional()]

    def _get_translations(self):
        return Translations()

    def _check_prefix(self):
        if self.issued_by.data != 'own':
            len_first_digit = len(self.first_digit.data)
            len_following = len(self.following_2to4_digits.data)
            if len_first_digit == 0 and len_following == 0:
                return True
            else:
                raise ValidationError(u'コード管理元が自社でない場合、接頭辞は指定できません')

        query = DiscountCodeSetting.filter_by(
            organization_id=self.organization_id,
            first_digit=self.first_digit.data,
            following_2to4_digits=self.following_2to4_digits.data
        )
        cnt = int(query.count())
        limit = 0
        if len(self.id.data) != 0:
            limit = 1

        if cnt > limit:
            raise ValidationError(u'すでに使用されている組み合わせです')

    def validate_first_digit(self):
        self._check_prefix()

    def validate_following_2to4_digits(self):
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
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
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
    condition_price_amount = TextField(
        validators=[
            Required(),
            Length(max=8, message=u'8桁以内で入力してください'),
        ]
    )
    condition_price_more_or_less = SelectField(
        validators=[Required()],
        choices=[
            ('less', u'以下')
        ],
        coerce=str
    )
    benefit_amount = TextField(
        validators=[
            Required(),
            Length(max=8, message=u'8桁以内で入力してください'),
        ]
    )
    benefit_unit = SelectField(
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
    )
    status = HiddenField(
        label=u'状態',
    )
    first_4_digits = HiddenField(
        label=u'頭4文字',
    )
    valid_term = HiddenField(
        label=u'有効期間',
    )
