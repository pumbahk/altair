# -*- coding: utf-8 -*-

import csv
import os
from datetime import datetime

from wtforms import (TextField, PasswordField, TextAreaField, DateField, DateTimeField,
                     SelectField, SubmitField, HiddenField, BooleanField, FileField, IntegerField)
from wtforms.validators import Required, Email, Length, NumberRange, EqualTo, Optional, ValidationError
from wtforms.widgets import CheckboxInput
from wtforms import Form

from paste.util.multidict import MultiDict
from newsletter.newsletters.models import Newsletter
from altair.formhelpers.filters import replace_ambiguous
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
        ], filters=[replace_ambiguous])
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
    subscriber_count = HiddenField(u'送信件数', validators=[Optional()], default='1')
    force_upload = IntegerField(
        label=u'エラーリストを無視',
        default=0,
        widget=CheckboxInput(),
    )
    start_date = DateField(u'送信日', validators=[
        Required(u'入力してください')
        ], format='%Y-%m-%d')
    start_time = DateTimeField(u'送信時間', validators=[], format='%H:%M', default=datetime.now().replace(hour=12, minute=0))
    start_on   = DateTimeField(u'送信日時', validators=[], format='%Y-%m-%d %H:%M:%S')
    created_at = DateTimeField(u'作成日時')
    updated_at = DateTimeField(u'更新日時')

    def __init__(self, *args, **kw):
        if args and args[0].get('start_date'):
            # set start_on
            args[0].add('start_on', args[0].get('start_date') + ' ' + args[0].get('start_time') + ':00')

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

    def validate_start_on(form, field):
        if field.data is not None and field.data < datetime.now() and form.status.data != 'completed':
            raise ValidationError(u'過去の日付を指定することはできません')

    def validate_subscriber_file(form, field):
        if hasattr(field.data, 'file'):
            if Newsletter.encode(field.data.file.read()) == False:
                 raise ValidationError(u'CSVデータが不正です')
            field.data.file.seek(0)

            if form.force_upload.data:
                 return

            csv_reader = csv.DictReader(field.data.file)
            error_email = []
            try:
                for row in csv_reader:
                    if not ('email' in row and Newsletter.validate_email(row['email'])):
                        error_email.append(u'<li>%s</li>' % row)
                else:
                    field.data.file.seek(0)
            except Exception, e:
                raise ValidationError(u'CSVデータが不正です %s' % e)
            if error_email:
                raise ValidationError(u'CSVデータが不正です (emailフォーマットエラー:%d件)<ul>%s</ul>' % (len(error_email), ''.join(error_email)))
