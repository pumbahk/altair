# -*- coding: utf-8 -*-

from deform.widget import SelectWidget
from colander import MappingSchema, SchemaNode, String, Int, DateTime, Bool, Decimal, Float
from ticketing.models.master import Prefecture

class EventForm(MappingSchema):
    start_on            = SchemaNode(DateTime()   , title=u'開始日')
    end_on              = SchemaNode(DateTime()   , title=u'終了日')
    code                = SchemaNode(String()   , title=u'公演コード')
    title               = SchemaNode(String()   , title=u'タイトル')
    abbreviated_title   = SchemaNode(String()   , title=u'タイトル略')
    margin_ratio        = SchemaNode(Float()    , title=u'マージン')
    printing_fee        = SchemaNode(Decimal()  , title=u'印刷手数料')
    registration_fee    = SchemaNode(Decimal()  , title=u'登録手数料')
