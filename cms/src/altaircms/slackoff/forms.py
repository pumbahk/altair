# -*- coding:utf-8 -*-
from wtforms.form import Form
from wtforms import fields
from wtforms import widgets
from wtforms import validators
from altaircms.event.models import Event
from altaircms.lib.formhelpers import dynamic_query_select_field_factory
from altaircms.helpers.formhelpers import required_field

class PerformanceForm(Form):
    backend_performance_id = fields.IntegerField(validators=[required_field()], label=u"バックエンド管理番号")
    event = dynamic_query_select_field_factory(Event, allow_blank=False, label=u"イベント")
    title = fields.TextField(label=u"講演タイトル")
    venue = fields.TextField(label=u"開催場所")
    open_on = fields.DateTimeField(label=u"開場時間", validators=[required_field()])
    start_on = fields.DateTimeField(label=u"開始時間", validators=[required_field()])
    close_on = fields.DateTimeField(label=u"終了時間", validators=[required_field()])

class TicketForm(Form):
    orderno = fields.IntegerField(label=u"表示順序", validators=[required_field()])
    event = dynamic_query_select_field_factory(Event, allow_blank=False, label=u"イベント") ## performance?
    price = fields.IntegerField(validators=[required_field()], label=u"料金")
    seattype = fields.TextField(validators=[required_field()], label=u"席種／グレード")
