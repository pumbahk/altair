# coding: utf-8
from wtforms.form import Form
from wtforms import fields
from wtforms import widgets
from wtforms import validators

from . import SUPPORTED_CLASSIFIER

class TagSearchForm(Form):
    query = fields.TextField(label=u"検索タグ名")
    classifier = fields.SelectField(label=u"検索対象",choices=[(x, x) for x in SUPPORTED_CLASSIFIER])
    # classifier = fields.TextField(label=u"検索対象") # hidden field?, multiple select field?
    # classifier = fields.SelectMultipleField(label=u"検索対象",choices=[(x, x) for x in SUPPORTED_CLASSIFIER])

    ## 公開/非公開？

## tag form
class TagForm(Form):
    tags = fields.TextField(label=u"タグ(区切り文字:\",\")")
    public_status = fields.BooleanField(default=False)

class PublicTagForm(Form):
    tags = fields.TextField(label=u"公開タグ(区切り文字:\",\")")
    public_status = fields.HiddenField(default=True)

class PrivateTagForm(Form):
    tags = fields.TextField(label=u"非公開タグ(区切り文字:\",\")")
    public_status = fields.HiddenField(default=False)
