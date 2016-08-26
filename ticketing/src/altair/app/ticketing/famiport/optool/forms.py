# -*- coding: utf-8 -*-

import re
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
from wtforms.validators import Required, Length, Optional, EqualTo
from wtforms.compat import iteritems
from wtforms import HiddenField, ValidationError

class LoginForm(OurForm):
    user_name = OurTextField(
        validators=[
            Required(),
            Length(max=32)
            ],
        label=u'ユーザ名'
        )
    password = OurTextField(
        widget=OurPasswordInput(),
        validators=[
            Required()
            ],
        label=u'パスワード'
        )

class ChangePassWordForm(OurForm):
    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        super(ChangePassWordForm, self).__init__(formdata, obj, prefix, **kwargs)
        for name, field in iteritems(self._fields):
            if name in kwargs:
                field.data = kwargs[name]

    user_id = HiddenField(
        validators=[Optional()]
    )
    password = OurTextField(
        widget=OurPasswordInput(),
        validators=[Required()],
        label=u'パスワード'
    )
    new_password = OurTextField(
        widget=OurPasswordInput(),
        validators=[
            Required(),
            Length(min=7, message=u'パスワードは7桁以上で設定してください。')
        ],
        label=u'新しいパスワード'
    )
    new_password_confirm = OurTextField(
        widget=OurPasswordInput(),
        validators=[
            Required(),
            EqualTo('new_password', message=u'新しいパスワードと一致していない。')
        ],
        label=u'新しいパスワードの確認'
    )

    def validate_new_password(form, field):
        pattern = r'^(?=.*[0-9])(?=.*[a-zA-Z])([a-zA-Z0-9]+)$'
        if not re.match(pattern, field.data):
            raise ValidationError(u'パスワードは数字と英文字の両方を含む7文字以上で設定ください。')

        if form.password.data == field.data:
            raise ValidationError(u'ご利用しているパスワードと同じな値に設定できません。')


class AccountReminderForm(OurForm):
    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        super(AccountReminderForm, self).__init__(formdata, obj, prefix, **kwargs)
        for name, field in iteritems(self._fields):
            if name in kwargs:
                field.data = kwargs[name]

    user_name = OurTextField(
        validators=[
            Required(),
            Length(max=32)
        ],
        label=u'ユーザ名'
    )
    email = OurTextField(
        validators=[
            Required(),
            Length(max=120)
        ],
        label=u'EMailアドレス'
    )

class SearchReceiptForm(OurForm):
    barcode_no = OurTextField(
        label=u'払込票番号：',
        validators=[
            Optional(),
            Length(min=13, max=13, message=u'払込票番号は13文字以内で入力して下さい')
        ]
    )
    reserve_number = OurTextField(
        label=u'引換票番号(予約番号)：',
        validators=[
            Optional(),
            Length(min=13, max=13, message=u'引換票番号は13文字以内で入力して下さい')
        ]
    )
    management_number = OurTextField(
        label=u'管理番号：',
        validators=[
            Optional(),
            Length(min=9, max=9, message=u'管理番号は半角数字9文字で入力してください'),
        ]
    )
    barcode_number = OurTextField(
        label=u'バーコード番号：',
        validators=[
            Optional(),
            Length(min=13, max=13, message=u'バーコードは半角数字13文字で入力してください')
        ]
    )
    customer_phone_number = OurTextField(
        label=u'電話番号(ハイフンなし)：',
        validators=[
            Optional(),
            Length(min=9, max=11, message=u'電話番号は9-11文字で入力して下さい')
        ]
    )
    shop_code = OurTextField(
        label=u'店番：',
        validators=[
            Optional(),
            Length(min=5, max=5, message=u'店番は半角数字5文字で入力して下さい')
        ]
    )
    shop_name = OurTextField(
        label=u'店名：',
    )
    completed_from = OurTextField(
        label=u'入金・発券日：',
    )
    completed_to = OurTextField(
        label=u'販売終了日',
    )


class SearchPerformanceForm(OurForm):
    event_id = OurTextField(
        label=u'興行ID：',
    )
    event_code_1 = OurTextField(
        label=u'興行コード：',
        validators=[
            Optional(),
            Length(min=6, max=6, message=u'興行コードは半角数字6文字で入力してください')
        ]
    )
    event_code_2 = OurTextField(
        label=u'興行サブコード：',
        validators=[
            Optional(),
            Length(min=4, max=4, message=u'興行サブコードは半角数字4文字で入力してください')
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

    # def validate_event_code_2(form, field):
    #     if not form.event_code_1.data and form.event_code_2.data:
    #         raise ValidationError(u'code_1とcode_2セットで入力要')

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
            Required(message=u'理由コードは必須です'),
        ],
    )
    cancel_reason_text = OurTextAreaField(
        label=u'理由備考：',
        validators=[
            Required(message=u'理由備考は必須です'),
        ]
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

class SearchRefundPerformanceForm(OurForm):
    before_refund = OurBooleanField(
        label=u'払戻期間前',
    )
    during_refund = OurBooleanField(
        label=u'払戻期間中',
    )
    after_refund = OurBooleanField(
        label=u'払戻期間後',
    )
    performance_from = OurTextField(
        label=u'公演日：',
    )
    performance_to = OurTextField(
        label=u'公演日：',
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
            Length(min=1, max=5, message=u'払戻店番は半角数字5文字以内で入力してください')
        ]
    )
    event_code = OurTextField(
        label=u'興行コード:',
        validators=[
            Optional(),
            Length(min=6, max=6, message=u'興行コードは半角数字6文字で入力してください')
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
