# -*- coding: utf-8 -*-

from altair.formhelpers.form import OurForm
from altair.formhelpers.fields import OurTextField, DateTimeField
from altair.formhelpers.widgets import OurPasswordInput, OurTextInput, OurDateWidget
from altair.formhelpers import Max, after1900
from wtforms.validators import Required, Length, Optional
from wtforms import ValidationError

class LoginForm(OurForm):
    user_name = OurTextField(
        validators=[
            Required(),
            Length(max=32)
            ]
        )
    password = OurTextField(
        widget=OurPasswordInput(),
        validators=[
            Required()
            ]
        )

class SearchReceiptForm(OurForm):
    barcode_no = OurTextField(
        label=u'払込票番号：',
    )
    exchange_number = OurTextField(
        label=u'引換票番号：',
    )
    famiport_order_identifier = OurTextField(
        label=u'管理番号：',
    )
    barcode_number = OurTextField(
        label=u'バーコード番号：',
    )
    customer_phone_number = OurTextField(
        label=u'電話番号：',
    )
    shop_code = OurTextField(
        label=u'店番：'
    )


class SearchPerformanceForm(OurForm):
    event_id = OurTextField(
        label=u'興行ID：',
    )
    event_code_1 = OurTextField(
        label=u'興行コード：',
        validators=[
            Length(max=6, message=u'6文字以内で入力してください')
        ]
    )
    event_code_2 = OurTextField(
        label=u'興行サブコード：',
        validators=[
            Length(max=4, message=u'4文字以内で入力してください')
        ]
    )
    event_name_1 = OurTextField(
        label=u'興行名：',
    )
    performance_name = OurTextField(
        label=u'公演名：',
    )
    venue_name = OurTextField(
        label=u'会場名：',
    )
    performance_from = OurTextField(
        label=u'公演日：',
    )
    performance_to = OurTextField(
        label=u'公演日：',
    )

    def validate_event_code_2(form, field):
        if not form.event_code_1.data and form.event_code_2.data:
            raise ValidationError(u'code_1とcode_2セットで入力要')