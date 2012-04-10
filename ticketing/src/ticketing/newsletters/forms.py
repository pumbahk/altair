# -*- coding: utf-8 -*-

from wtforms import (TextField, PasswordField, TextAreaField, DateField, DateTimeField,
                     SelectField, SubmitField, HiddenField, BooleanField, FileField)
from wtforms.validators import Required, Email, Length, NumberRange, EqualTo, optional, ValidationError
from wtforms import Form

from models import Newsletter

from paste.util.multidict import MultiDict
from datetime import datetime
import csv
import logging
import os
log = logging.getLogger(__name__)

class NewslettersForm(Form):
    subject             = TextField(u'件名', validators=[
                              Required(u'入力してください'),
                              Length(max=60, message=u'60文字以内で入力してください'),
                          ])
    description         = TextAreaField(u'本文', validators=[
                              Required(u'入力してください'),
                              Length(max=50000, message=u'50000文字以内で入力してください'),
                          ])
    status              = SelectField(u'状態', validators=[], choices=[
                              ('editing', u'作成中'),
                              ('waiting', u'送信予約中'),
                              ('completed', u'送信完了'),
                          ], default='editing')
    start_date          = DateField(u'送信日', validators=[Required(u'入力してください')], format='%Y-%m-%d')
    start_time          = DateTimeField(u'送信時間', validators=[], format='%H:%M')
    start_on            = DateTimeField(u'送信日時', validators=[], format='%Y-%m-%d %H:%M:%S')
    subscriber_file     = FileField(u'送信先リスト', validators=[])
    subscriber_count    = TextField(u'送信件数', validators=[])

    def __init__(self, *args, **kw):
        if args:
            # create start_on
            args[0].add('start_on', args[0].get('start_date') + ' ' + args[0].get('start_time') + ':00')

            # create subscriber_count
            subscriber_file = args[0].get('subscriber_file')
            count = 0 
            if hasattr(subscriber_file, 'file'):
                fields = ['id', 'name', 'email']
                for row in csv.DictReader(subscriber_file.file, fields):
                    if Newsletter.validateEmail(row['email']): count += 1
                else:
                    subscriber_file.file.seek(0)
            args[0].add('subscriber_count', str(count))

        Form.__init__(self, *args, **kw)

    def process(self, formdata=None, obj=None, **kwargs):
        if formdata != None and formdata.get('start_on') != None:
            try:
                start_on = datetime.strptime(formdata.get('start_on'), '%Y-%m-%d %H:%M:%S')
                formdata.update({'start_date':start_on.strftime('%Y-%m-%d')})
                formdata.update({'start_time':start_on.strftime('%H:%M')})
            except:
                log.error('start_on date parse error')

        Form.process(self, formdata, obj, **kwargs)

    def validate_status(form, field):
        if field.data == 'waiting' and form.subscriber_count.data == '0':
            raise ValidationError(u'送信先リストが0件なので送信予約できません')

    def validate_start_on(form, field):
        if field.data < datetime.now():
            raise ValidationError(u'過去の日付を指定することはできません')

    def validate_subscriber_file(form, field):
        if hasattr(field.data, 'file'):
            print '=========================================='
            print vars(field.data)
            fields = ['id', 'name', 'email']
            for row in csv.DictReader(field.data.file, fields):
                print '=========================================='
                print row
                if not row['id'].isdigit() or len(row['name']) == 0 or not Newsletter.validateEmail(row['email']):
                    raise ValidationError(u'CSVデータが不正です')
            else:
                field.data.file.seek(0)

