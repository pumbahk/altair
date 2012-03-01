# coding: utf-8
import colander
from wtforms import fields, validators
from wtforms.form import Form


class Event(colander.MappingSchema):
    title = colander.SchemaNode(colander.String())
    subtitle = colander.SchemaNode(colander.String(), missing=None)
    description = colander.SchemaNode(colander.String(), missing=None)
    place = colander.SchemaNode(colander.String(), missing=None)
    inquiry_for = colander.SchemaNode(colander.String(), missing='')
    event_open = colander.SchemaNode(colander.Date(), missing=None)
    event_close = colander.SchemaNode(colander.Date(), missing=None)
    deal_open = colander.SchemaNode(colander.Date(), missing=None)
    deal_close = colander.SchemaNode(colander.Date(), missing=None)
    is_searchable = colander.SchemaNode(colander.Integer(), missing=1, default=1)

event_schema = Event()


class EventForm(Form):
    title = fields.TextField(label=u'タイトル', validators=[validators.Required()])
    subtitle = fields.TextField(label=u'サブタイトル')
    description = fields.TextAreaField(label=u'説明')
    place = fields.TextField(label=u'開催場所')
    inquiry_for = fields.TextField(label=u'問い合わせ先')
    event_open = fields.DateTimeField(label=u'イベント開始日')
    event_close = fields.DateTimeField(label=u'イベント終了日')
    deal_open = fields.DateTimeField(label=u'販売開始日')
    deal_close = fields.DateTimeField(label=u'販売終了日')
    is_searchable = fields.BooleanField(label=u'検索可否フラグ', default=False)



class EventRegisterForm(Form):
    jsonstring = fields.TextField(validators=[validators.Required()])
