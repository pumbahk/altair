# coding: utf-8
from wtforms import fields, validators
from wtforms.form import Form
from altaircms.helpers.formhelpers import required_field, append_errors


class EventForm(Form):
    title = fields.TextField(label=u'タイトル', validators=[required_field()])
    subtitle = fields.TextField(label=u'サブタイトル')
    backend_id = fields.IntegerField(validators=[required_field()], label=u"バックエンド管理番号")
    description = fields.TextAreaField(label=u'説明')
    place = fields.TextField(label=u'開催場所')
    inquiry_for = fields.TextField(label=u'問い合わせ先')
    event_open = fields.DateTimeField(label=u'イベント開始日', validators=[required_field()])
    event_close = fields.DateTimeField(label=u'イベント終了日', validators=[required_field()])
    deal_open = fields.DateTimeField(label=u'販売開始日', validators=[required_field()])
    deal_close = fields.DateTimeField(label=u'販売終了日', validators=[required_field()])
    is_searchable = fields.BooleanField(label=u'検索対象に含める', default=True)

    def validate(self, **kwargs):
        data = self.data
        if data["event_open"] > data["event_close"]:
            append_errors(self.errors, "event_open", u"イベント終了日よりも後に設定されてます")
        if data["deal_open"] > data["deal_close"]:
            append_errors(self.errors, "deal_open", u"販売終了日よりも後に設定されてます")
        return not bool(self.errors)

    __display_fields__ = [u"title", u"subtitle", 
                          u"backend_id", 
                          u"description", u"place", u"inquiry_for", 
                          u"event_open", u"event_close", 
                          u"deal_open", u"deal_close", 
                          u"is_searchable"]
