# coding: utf-8

from altaircms.helpers.formhelpers import MaybeDateTimeField
from wtforms import fields, validators
from wtforms.form import Form
from wtforms import widgets

from altaircms.helpers.formhelpers import required_field, append_errors
from .models import Event
from ..page.models import PageSet
from ..models import Category
from altaircms.lib.formhelpers import dynamic_query_select_field_factory

class EventForm(Form):
    title = fields.TextField(label=u'タイトル', validators=[required_field()])
    subtitle = fields.TextField(label=u'サブタイトル')
    backend_id = fields.IntegerField(validators=[required_field()], label=u"バックエンド管理番号")
    description = fields.TextAreaField(label=u'説明')
    inquiry_for = fields.TextField(label=u'問い合わせ先', widget=widgets.TextArea())
    notice = fields.TextField(label=u"説明／注意事項", widget=widgets.TextArea())
    performers = fields.TextField(label=u"出演者リスト", widget=widgets.TextArea())
    ticket_pickup = fields.TextField(label=u"チケット引き取り方法", widget=widgets.TextArea())
    ticket_payment = fields.TextField(label=u"支払い方法", widget=widgets.TextArea())
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

    def object_validate(self, obj=None):
        data = self.data
        qs = Event.query.filter(Event.backend_id == data["backend_id"])
        if obj:
            qs = qs.filter(Event.backend_id != obj.backend_id)
        if qs.count() >= 1:
            append_errors(self.errors, "backend_id", u"バックエンドIDが重複しています。(%s)" % data["backend_id"])
        return not bool(self.errors)

    __display_fields__ = [u"title", u"subtitle", 
                          u"backend_id", 
                          u"description", u"performers", u"inquiry_for", "notice", "ticket_payment", "ticket_pickup", 
                          u"event_open", u"event_close", 
                          u"deal_open", u"deal_close", 
                          u"is_searchable"]

class EventSearchForm(Form):
    freeword = fields.TextField(label=u'タイトル, サブタイトルなど')
    is_vetoed = fields.BooleanField(label=u"検索対象から除外したものだけを探す")
    event_open = MaybeDateTimeField(label=u'イベント開始日')
    # op_choice = ([("lte", u"より前") ,("eq", u"その日"), ("gte", u"より後")]) #lt, gt?
    op_choice = ([("lte", u"より前") , ("gte", u"より後")]) #lt, gt?
    event_open_op = fields.SelectField(choices=op_choice)
    event_close = MaybeDateTimeField(label=u'イベント終了日')
    event_close_op = fields.SelectField(choices=op_choice)
    deal_open = MaybeDateTimeField(label=u'販売開始日')
    deal_open_op = fields.SelectField(choices=op_choice)
    deal_close = MaybeDateTimeField(label=u'販売終了日')
    deal_close_op = fields.SelectField(choices=op_choice)
    created_at = MaybeDateTimeField(label=u'作成日')
    created_at_op = fields.SelectField(choices=op_choice)
    updated_at = MaybeDateTimeField(label=u'更新日')
    updated_at_op = fields.SelectField(choices=op_choice)
    category = dynamic_query_select_field_factory(
        Category, allow_blank=True, label=u"カテゴリ",
        get_label=lambda obj: obj.label or u"--なし--")

class EventTakeinPageForm(Form):
    pageset = dynamic_query_select_field_factory(
        PageSet, allow_blank=False, label=u"取り込むページ",
        get_label=lambda obj: u"%s %s" % (obj.name, u"(イベント配下)" if obj.event_id else u""))

    def validate_pageset(form, field):
        if field.data.category:
            raise validators.ValidationError(u"トップ／カテゴリトップのページは配下におくことができません")
