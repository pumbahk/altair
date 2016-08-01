# -*- coding: utf-8 -*-

from wtforms import TextField, TextAreaField, HiddenField, SelectField, FieldList, FormField, Form
from wtforms.validators import Length, Optional, ValidationError
from wtforms.widgets.core import HTMLString
from wtforms.widgets import ListWidget, html_params
from wtforms.compat import text_type

from altair.formhelpers import Translations, Required, BugFreeSelectField, OurTextField, OurHiddenField, \
    zero_as_none, after1900, OurDateTimeWidget, OurBooleanField
from altair.formhelpers.fields import DateTimeField
from altair.app.ticketing.users.models import Announcement
from datetime import date, datetime, timedelta
from altair.formhelpers.validators import DateTimeInRange

now = datetime.now()
limit = now + timedelta(hours=2) - timedelta(minutes=now.minute, seconds=now.second)
send_after_range = DateTimeInRange(from_=limit)

class ParameterForm(Form):

    key = HiddenField()
    value = TextField()

class SimpleListWidget(ListWidget):
    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        html = ['<div>']
        for subfield in field:
            html.append('<div>%s</div>' % subfield())
        html.append('</div>')
        return HTMLString(''.join(html))

class KeyValueWidget(object):

    def __init__(self, style=""):
        self.style = style

    def __call__(self, field, **kwargs):
        html = ['<table %s>' % html_params(style=self.style)]
        hidden = ''
        for subfield in field:
            if subfield.type == 'HiddenField':
                hidden += '<th>%s%s</th>' % (text_type(subfield), text_type(subfield.data))
            else:
                html.append('%s<td>%s</td>' % (hidden, text_type(subfield)))
                hidden = ''
        if hidden:
            html.append(hidden)
        html.append('</table>')
        return HTMLString(''.join(html))

class AnnouncementForm(Form):

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata, obj, prefix, **kwargs)

    def _get_translations(self):
        return Translations()

    def update_obj(self, announce):
        announce.subject = self.subject.data
        announce.message = self.message.data
        announce.parameters = dict()
        for kv in self.parameters.data:
            announce.parameters[kv["key"]] = text_type(kv["value"])
        announce.send_after = self.send_after.data
        announce.is_draft = self.is_draft.data
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

    parameters = FieldList(
        FormField(ParameterForm, widget=KeyValueWidget(style="background-color: transparent;")),
        label=u'パラメータ',
        widget=SimpleListWidget(),
    )

    is_draft = OurBooleanField(
        label=u'下書き',
        default=False,
        validators=[Required()],
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
