# -*- coding: utf-8 -*-

from altair.formhelpers.form import OurForm
from altair.formhelpers.fields import (
    OurTextField,
    DateTimeField,
    OurRadioField,
    OurSelectField,
    OurTextAreaField,
    OurBooleanField
)
from altair.formhelpers.widgets import (
    OurPasswordInput,
    OurTextInput,
    OurDateWidget,
)
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
        validators=[
            Optional(),
            Length(9, message=u'管理番号は9桁で入力してください'),
        ]
    )
    barcode_number = OurTextField(
        label=u'バーコード番号：',
    )
    customer_phone_number = OurTextField(
        label=u'電話番号：',
    )
    shop_code = OurTextField(
        label=u'店番：',
    )
    shop_name = OurTextField(
        label=u'店名：',
    )
    sales_from = OurTextField(
        label=u'販売開始日：',
    )
    sales_to = OurTextField(
        label=u'販売終了日',
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

class RebookOrderForm(OurForm):
    cancel_reason_code = OurSelectField(
        label=u'理由コード：',
        choices=[
            ('910', u'【910】同席番再予約（店舗都合）'),
            ('911', u'【911】同席番再予約（お客様都合）'),
            ('912', u'【912】同席番再予約（強制成立）'),
            ('913', u'【913】再発券（店舗都合）'),
            ('914', u'【914】その他'),
        ],
        validators=[
            Required(),
        ],
    )
    cancel_reason_text = OurTextAreaField(
        label=u'理由備考：',
    )
    old_num_type = OurTextField(
        label=u'旧番号種類：',
    )
    old_num = OurTextField(
        label=u'旧番号：',
        validators=[
            Required(),
        ]
    )

class RefundTicketSearchForm(OurForm):

    before_refund = OurBooleanField(
        label=u'払戻期間前',
        validators=[
            Optional()
        ],
    )

    during_refund = OurBooleanField(
        label=u'払戻期間中',
        validators=[
            Optional()
        ],
    )

    after_refund = OurBooleanField(
        label=u'払戻期間後',
        validators=[
            Optional()
        ],
    )

    management_number = OurTextField(
        label=u'管理番号:',
        validators=[
            Optional(),
            Length(min=9, max=9, message=u'管理番号は半角数字9文字で入力してください')
        ],

    )
    barcode_number = OurTextField(
        label=u'バーコード:',
        validators=[
            Optional(),
            Length(min=13, max=13, message=u'バーコードは半角数字13文字で入力してください')
        ]
    )
    refunded_shop_code = OurTextField(
        label=u'払戻店番:',
        validators=[
            Optional(),
            Length(min=5, max=5, message=u'払戻店番は半角数字5文字で入力してください')
        ]
    )
    event_code = OurTextField(
        label=u'興行コード:',
        validators=[
            Optional(),
            Length(min=4, max=6, message=u'興行コードは半角数字6文字で入力してください')
        ]
    )
    event_subcode = OurTextField(
        label=u'興行サブコード:',
        validators=[
            Optional(),
            Length(min=4, max=4, message=u'興行サブコードは半角数字4文字で入力してください')
        ]
    )
    performance_start_date = OurTextField(
        id="datepicker1",
        label=u'公演日:',
        validators=[
            Optional()
        ],
    )
    performance_end_date = OurTextField(
        id="datepicker2",
        label=u'〜',
        validators=[
            Optional()
        ],
    )
