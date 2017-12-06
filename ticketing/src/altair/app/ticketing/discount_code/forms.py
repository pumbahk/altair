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
        """
        入力された4桁の接頭辞の妥当性を確認。
        コード管理元が自社でない場合は、接頭辞は空文字であること。
        自社の場合は、新たに登録しようとしている組み合わせが存在しないことを確認する。
        :return: エラーメッセージ
        """
        if self.issued_by.data != 'own':
            len_first_digit = len(self.first_digit.data)
            len_following = len(self.following_2to4_digits.data)
            if len_first_digit == 0 and len_following == 0:
                return True
            else:
                raise ValidationError(u'コード管理元が自社でない場合、接頭辞は指定できません')

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
