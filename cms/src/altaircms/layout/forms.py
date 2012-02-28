# coding: utf-8
from wtforms import fields, validators
from wtforms.form import Form

class LayoutForm(Form):
    title = fields.TextField(u'タイトル', validators=[validators.Required()])
    blocks = fields.TextField(u'ブロック', validators=[validators.Required()])
    template_filename = fields.TextField(u'テンプレートファイル名', validators=[validators.Required()])
