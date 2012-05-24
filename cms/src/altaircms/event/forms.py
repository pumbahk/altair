# coding: utf-8
from wtforms import fields, validators
from wtforms.form import Form
from altaircms.helpers.formhelpers import required_field

class EventForm(Form):
    title = fields.TextField(label=u'タイトル', validators=[required_field()])
    subtitle = fields.TextField(label=u'サブタイトル')
    description = fields.TextAreaField(label=u'説明')
    place = fields.TextField(label=u'開催場所')
    inquiry_for = fields.TextField(label=u'問い合わせ先')
    event_open = fields.DateTimeField(label=u'イベント開始日', validators=[required_field()])
    event_close = fields.DateTimeField(label=u'イベント終了日', validators=[required_field()])
    deal_open = fields.DateTimeField(label=u'販売開始日', validators=[required_field()])
    deal_close = fields.DateTimeField(label=u'販売終了日', validators=[required_field()])
    is_searchable = fields.BooleanField(label=u'検索可否フラグ', default=False)
