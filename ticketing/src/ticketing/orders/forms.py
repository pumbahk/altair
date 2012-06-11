# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import HiddenField, TextField, DateTimeField, SelectField, TextAreaField
from wtforms.validators import Optional,Required

class OrderForm(Form):

    id = HiddenField(
        label=u'ID',
        validators=[Optional()],
    )
    total_amount = HiddenField(
        label=u'合計',
        validators=[Optional()],
    )
    created_at = HiddenField(
        label=u'受注日時',
        validators=[Optional()],
    )

class SejOrderForm(Form):

    id = HiddenField(
        label=u'ID',
        validators=[Optional()],
    )
    order_id= TextField(
        label=u'オーダーID',
        validators=[Optional()],
    )
    shop_id= TextField(
        label=u'ショップID',
        default=30520,
        validators=[Optional()],
    )
    shop_name= TextField(
        label=u'ショップ名',
        default=u'楽天チケット',
        validators=[Optional()],
    )
    contact_01= TextField(
        label=u'連絡先１',
        validators=[Optional()],
    )
    contact_02= TextField(
        label=u'連絡先２',
        validators=[Optional()],
    )
    user_name= TextField(
        label=u'ユーザー名',
        validators=[Optional()],
    )
    user_name_kana= TextField(
        label=u'ユーザー名（カナ）',
        validators=[Optional()],
    )
    tel= TextField(
        label=u'ユーザー電話番号',
        validators=[Optional()],
    )
    zip_code= TextField(
        label=u'ユーザー郵便番号',
        validators=[Optional()],
    )
    email= TextField(
        label=u'ユーザーEmail',
        validators=[Optional()],
    )

    total_price = TextField(
        label=u'合計',
        validators=[Required()],
    )
    ticket_price = TextField(
        label=u'チケット金額',
        validators=[Required()],
    )
    commission_fee = TextField(
        label=u'手数料',
        validators=[Required()],
    )
    ticketing_fee = TextField(
        label=u'発券手数料',
        validators=[Required()],
    )

    payment_due_at = DateTimeField(
        label=u'支払い期限',
        validators=[Optional()],
    )
    ticketing_start_at = DateTimeField(
        label=u'発券開始',
        validators=[Optional()],
    )
    ticketing_due_at = DateTimeField(
        label=u'発券期限',
        validators=[Optional()],
    )
    regrant_number_due_at = DateTimeField(
        label=u'SVC再付番期限',
        validators=[Required()],
    )

    payment_type = SelectField(
        label=u'支払い方法',
        choices=[(u'1', u'代引き'), (u'2', u'前払い(後日発券)'), (u'3', u' 代済発券'), (u'4', u' 前払いのみ')],
        validators=[Optional()],
    )

    update_reason = SelectField(
        label=u'更新理由',
        choices=[(u'1', u'項目変更'), (u'2', u'公演中止')],
        validators=[Optional()],
    )


class SejTicketForm(Form):
    ticket_type = SelectField(
        label=u'チケット区分',
        choices=[(u'1', u'本券（バーコード付き）'), (u'2', u'本券'), (u'3', u' 副券（バーコード付き）'), (u'4', u' 副券')],
        validators=[Optional()],
    )
    event_name              = TextField(
        label=u'イベント名',
        validators=[Required()],
    )
    performance_name        = TextField(
        label=u'パフォーマンス名',
        validators=[Required()],
    )
    performance_datetime    = DateTimeField(
        label=u'発券期限',
        validators=[Optional()],
    )
    ticket_template_id      = TextField(
        label=u'テンプレートID',
        validators=[Required()],
    )
    ticket_data_xml         = TextAreaField(
        label=u'XML',
        validators=[Required()],
    )

