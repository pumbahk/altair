# -*- coding: utf-8 -*-
from wtforms.validators import ValidationError, email, Required
from wtforms import Form, TextField, TextAreaField, SelectField, HiddenField

class InquiryForm(Form):

    # --- Form
    username = TextField(label = u'お名前（漢字）※', validators=[Required(u'入力してください')])
    username_kana = TextField(label = u'お名前（カナ）※', validators=[Required(u'入力してください')])
    zip_no = TextField(label = u'郵便番号', validators=[Required(u'入力してください')])
    address = TextField(label = u'住所', validators=[Required(u'入力してください')])
    tel = TextField(label = u'電話番号', validators=[Required(u'入力してください')])
    mail = TextField(label = u'メールアドレス※', validators=[Required(u'入力してください'), email(u'メールアドレスに誤りがあります')])
    num = TextField(label = u'受付番号(RT00000～)')
    category = SelectField(label = u'カテゴリ※', choices=[
        (u"選択なし", u'選択してください'), (u'チケットについて', u'チケットについて'), (u'お支払い方法について', u'お支払い方法について'),
        (u'座席について', u'座席について'), (u'配送方法について', u'配送方法について'), (u'ご意見/ご感想', u'ご意見/ご感想'), (u'その他', u'その他')
    ],default=0)
    title = TextField(label = u'タイトル※', validators=[Required(u'入力してください')])
    body = TextAreaField(label = u'内容※', validators=[Required(u'入力してください')])

    # --- 表示用
    send = HiddenField(label = u'')

    def validate_category(form, field):
        if field.data == u"選択なし":
            raise ValidationError(u'選択してください')
        return
