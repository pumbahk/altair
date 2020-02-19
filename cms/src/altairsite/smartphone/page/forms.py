# -*- coding: utf-8 -*-
import re
from datetime import datetime, timedelta
from wtforms import Form, TextField, TextAreaField, SelectField, HiddenField
from wtforms.validators import ValidationError, email, Required

# ロボットを弾くため、お問い合わせを投稿させない時間
TIME_NOT_TO_POST = 2


class BaseForm(Form):
    username = TextField(label=u'お名前（漢字）', validators=[Required(u'入力してください')])
    username_kana = TextField(label=u'お名前（カナ）', validators=[Required(u'入力してください')])
    tel = TextField(label=u'電話番号', validators=[Required(u'入力してください')])
    mail = TextField(label=u'メールアドレス', validators=[Required(u'入力してください'), email(u'メールアドレスに誤りがあります')])
    title = TextField(label=u'タイトル', validators=[Required(u'入力してください')])
    body = TextAreaField(label=u'内容', validators=[Required(u'入力してください')])
    reception_number = TextField(label=u'受付番号')
    admission_time = HiddenField(label=u'入場時間', validators=[Required(u'入力してください')])
    zip_no = TextField(label=u'郵便番号')
    address = TextField(label=u'住所', validators=[Required(u'入力してください')])

    # --- 表示用
    send = HiddenField(label=u'')

    @staticmethod
    def validate_mail(form, field):
        if not field.data:
            raise ValidationError(u'メールアドレスを入力してください')

        email = field.data.strip()
        if re.match(r'^[a-zA-Z0-9_+\-*/=.]+@[^.][a-zA-Z0-9_\-.]*\.[a-z]{2,10}$', email) is not None:
            return True
        raise ValidationError(u'メールアドレスの形式が不正です。全角は使用できません。')

    @staticmethod
    def validate_admission_time(form, field):
        now = datetime.now()
        admission_time = datetime.strptime(field.data, '%Y/%m/%d %H:%M:%S')
        if admission_time + timedelta(seconds=TIME_NOT_TO_POST) < now:
            return
        raise ValidationError(u'不正な操作の可能性があります。')


class RtInquiryForm(BaseForm):
    # --- rakuten ticket inquiry Form
    category = SelectField(label=u'カテゴリ', choices=[
            (u"選択なし", u'選択してください'), (u'チケットについて', u'チケットについて'), (u'お支払い方法について', u'お支払い方法について'),
            (u'座席について', u'座席について'), (u'配送方法について', u'配送方法について'), (u'ご意見/ご感想', u'ご意見/ご感想'), (u'その他', u'その他')
         ], default=0)

    @staticmethod
    def validate_category(form, field):
        if field.data == u"選択なし":
            raise ValidationError(u'選択してください')
        return


class StInquiryForm(BaseForm):
    # ---SMA ticket inquiry Form
    app_status = TextField(label=u'申し込み状況')
    event_name = TextField(label=u'公演・イベント名')
    start_date = TextField(label=u"開催日時")

    category = SelectField(label=u'お問い合わせ項目', choices=[
        (u"選択なし", u'選択してください'), (u'会員登録', u'会員登録'), (u'申し込み', u'申し込み'),
        (u'支払い', u'支払い'), (u'受け取り', u'受け取り'), (u'変更', u'変更'), (u'リセール', u'リセール'),
        (u'その他', u'その他')
    ], default=0)

    @staticmethod
    def validate_category(form, field):
        if field.data == u"選択なし":
            raise ValidationError(u'選択してください')
        return
