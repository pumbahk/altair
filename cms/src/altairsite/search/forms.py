#-*- coding:utf-8 -*-
from wtforms import form
from wtforms import fields
from wtforms import widgets
from wtforms import validators

from .formparts import CheckboxListField
## todo:フリーワード
## todo:ジャンル
## todo:開催地
## todo:公演日
## todo:販売条件
## todo:付加サービス
## todo:発売日


class QueryPartForm(form.Form):
    query = fields.TextField(label=u"")
    query_cond = fields.RadioField(choices=[("intersection", u"全てを含む"), ("union", u"少なとも1つを含む")])


# def render_form(form):
#     for k in form.data.keys():
#         print unicode(getattr(form, k))

class FooForm(form.Form):
    foo = CheckboxListField(value="a,b,c")
