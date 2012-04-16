# -*- coding: utf-8 -*-

import csv
import os
from datetime import datetime

from wtforms import (TextField, PasswordField, TextAreaField, DateField, DateTimeField,
                     SelectField, SubmitField, HiddenField, BooleanField, FileField, IntegerField)
from wtforms.validators import Required, Email, Length, NumberRange, EqualTo, optional, ValidationError
from wtforms import Form

from paste.util.multidict import MultiDict
from newsletter.newsletters.models import Newsletter

import logging
log = logging.getLogger(__name__)

class NewslettersForm(Form):
    id = IntegerField(u'ID')
    subject = TextField(u'件名', validators=[
        Required(u'入力してください'),
        Length(max=60, message=u'60文字以内で入力してください'),
        ])
    description = TextAreaField(u'本文', validators=[
        Required(u'入力してください'),
        Length(max=50000, message=u'50000文字以内で入力してください'),
        ])
    type = SelectField(u'メール種別', validators=[], choices=[
        ('text', u'テキスト'),
        ('html', u'HTML'),
        ], default='text')
    status = SelectField(u'状態', validators=[], choices=[
        ('editing', u'作成中'),
        ('waiting', u'送信予約中'),
        ('completed', u'送信完了'),
        ], default='editing')
    sender_address = TextField(u'送信者アドレス', validators=[
        Required(u'入力してください'),
        Email(u'正しいメールアドレスを入力してください'),
        ])
    sender_name = TextField(u'送信者名', validators=[])
    subscriber_file = FileField(u'送信先リスト', validators=[])
    subscriber_count = TextField(u'送信件数', validators=[])
    start_date = DateField(u'送信日', validators=[
        Required(u'入力してください')
        ], format='%Y-%m-%d')
    start_time = DateTimeField(u'送信時間', validators=[], format='%H:%M')
    start_on   = DateTimeField(u'送信日時', validators=[], format='%Y-%m-%d %H:%M:%S')
    created_at = DateTimeField(u'作成日時')
    updated_at = DateTimeField(u'更新日時')

    def __init__(self, *args, **kw):
        if args:
            # set start_on
            args[0].add('start_on', args[0].get('start_date') + ' ' + args[0].get('start_time') + ':00')

            # set subscriber_count
            subscriber_file = args[0].get('subscriber_file')
            count = 0 
            if hasattr(subscriber_file, 'file'):
                for row in csv.DictReader(subscriber_file.file, Newsletter.csv_fields):
                    if Newsletter.validate_email(row['email']): count += 1
                else:
                    subscriber_file.file.seek(0)
            elif 'id' in args[0]:
                newsletter = Newsletter.get(args[0].get('id'))
                csv_file = os.path.join(Newsletter.subscriber_dir(), newsletter.subscriber_file())
                if os.path.exists(csv_file):
                    for row in csv.DictReader(open(csv_file), Newsletter.csv_fields):
                        count += 1

            args[0].add('subscriber_count', str(count))

        Form.__init__(self, *args, **kw)

    def process(self, formdata=None, obj=None, **kwargs):
        if formdata is not None and formdata.get('start_on') is not None:
            try:
                start_on = datetime.strptime(formdata.get('start_on'), '%Y-%m-%d %H:%M:%S')
                formdata.update({'start_date' : start_on.strftime('%Y-%m-%d')})
                formdata.update({'start_time' : start_on.strftime('%H:%M')})
            except:
                log.error('start_on date parse error')

        Form.process(self, formdata, obj, **kwargs)

    def validate_status(form, field):
        if field.data == 'waiting' and form.subscriber_count.data == '0':
            raise ValidationError(u'送信先リストが0件なので送信予約できません')

    def validate_start_on(form, field):
        if field.data is not None and field.data < datetime.now() and form.status.data != 'completed':
            raise ValidationError(u'過去の日付を指定することはできません')

    def validate_subscriber_file(form, field):
        if hasattr(field.data, 'file'):
            for row in csv.DictReader(field.data.file, Newsletter.csv_fields):
                if not Newsletter.validate_email(row['email']):
                    raise ValidationError(u'CSVデータが不正です')
            else:
                field.data.file.seek(0)

