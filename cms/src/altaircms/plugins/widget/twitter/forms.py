# -*- coding:utf-8 -*-
import wtforms.form as form
import wtforms.fields as fields
import wtforms.validators as validators
from . import models

class TwitterSearchDataInputForm(form.Form):
    search_query = fields.TextField(label=u"検索ワード")
    title = fields.TextField(label=u"タイトル")
    subject = fields.TextField(label=u"見出し") ## caption
    
