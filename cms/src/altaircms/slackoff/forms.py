# -*- coding:utf-8 -*-
from wtforms.form import Form
from wtforms import fields
from wtforms import widgets
from wtforms import validators
from altaircms.event.models import Event
from altaircms.lib.formhelpers import dynamic_query_select_field_factory

class PerformanceForm(Form):
    backend_performance_id = fields.IntegerField(validators=[validators.Required()], label=u"バックエンド管理番号")
    event = dynamic_query_select_field_factory(Event, allow_blank=False, label=u"イベント")
    title = fields.TextField(label=u"講演タイトル")
    venue = fields.TextField(label=u"開催場所")
    open_on = fields.DateTimeField(label=u"開場時間")
    start_on = fields.DateTimeField(label=u"開始時間")
    close_on = fields.DateTimeField(label=u"終了時間")

class TicketForm(Form):
    orderno = fields.IntegerField(label=u"表示順序")
    event = dynamic_query_select_field_factory(Event, allow_blank=False, label=u"イベント") ## performance?
    price = fields.IntegerField(validators=[validators.Required()], label=u"料金")
    seattype = fields.TextField(validators=[validators.Required()], label=u"席種／グレード")
