# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, TextAreaField, HiddenField, SelectField
from wtforms.validators import Length, Optional, ValidationError

from altair.formhelpers import Translations, Required, BugFreeSelectField,\
    zero_as_none, after1900, OurDateTimeWidget
from altair.formhelpers.fields import DateTimeField
from altair.app.ticketing.users.models import Announcement
from datetime import date, datetime, timedelta
from altair.formhelpers.validators import DateTimeInRange

now = datetime.now()
limit = now + timedelta(hours=2) - timedelta(minutes=now.minute, seconds=now.second)
send_after_range = DateTimeInRange(from_=limit)

class AnnouncementForm(Form):

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata, obj, prefix, **kwargs)

    def _get_translations(self):
        return Translations()

    def update_obj(self, announce):
        announce.subject = self.subject.data
        announce.message = self.message.data
        announce.send_after = self.send_after.data
        # TODO: check length of words
        announce.words = self.words.data
        announce.note = self.note.data

    note = TextAreaField(
        label=u'メモ (内部用)',
        validators=[
            Length(max=1000, message=u'1000文字以内で入力してください'),
        ]
    )

    subject = TextField(
        label=u'題名',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ],

    )

    message = TextAreaField(
        label=u'本文',
        validators=[
            Required(),
            Length(max=8000, message=u'8000文字以内で入力してください'),
        ]
    )

    send_after = DateTimeField(
        label=u'送信日時',
        validators=[Required(), send_after_range],
        widget=OurDateTimeWidget(omit_second=True)
        )

    words = HiddenField(
        label=u'お気に入りワードID',
        validators=[
            Required(),
            Length(max=1000, message=u'1000文字以内で入力してください'),
            # /^¥d+(,¥d+)*$/
        ]
    )
