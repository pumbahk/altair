# -*- coding: utf-8 -*-
from wtforms import Form
from wtforms import TextField, TextAreaField, SelectField, HiddenField
from wtforms.validators import Optional, Length, Optional, ValidationError, email, Required

class InquiryForm(Form):

    # --- Form
    name = TextField(label = u'お名前※', validators=[Required(u'入力してください')])
    mail = TextField(label = u'メールアドレス※', validators=[Required(u'入力してください'), email(u'メールアドレスに誤りがあります')])
    num = TextField(label = u'予約受付番号')
    category = SelectField(label = u'カテゴリ※', choices=[
        (0, u'選択してください'), (1, u'チケットについて'), (2, u'お支払い方法について'),
        (3, u'座席について'), (4, u'配送方法について'), (5, u'ご意見/ご感想'), (6, u'その他')
        ],default=0, coerce=int)
    title = TextField(label = u'タイトル※', validators=[Required(u'入力してください')])
    body = TextAreaField(label = u'内容※', validators=[Required(u'入力してください')])

    # --- 表示用
    send = HiddenField(label = u'')

    def validate_category(form, field):
        if field.data == 0:
            raise ValidationError(u'選択してください')
        return