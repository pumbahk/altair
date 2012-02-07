# coding: utf-8
import json

import colander
import deform
from deform.form import Form


def json_validator(node, value):
    try:
        json.loads(value)
    except ValueError:
        raise colander.Invalid(node, 'JSON object required')


class PageSchema(colander.MappingSchema):
    url = colander.SchemaNode(colander.String())
    title = colander.SchemaNode(colander.String())
    description = colander.SchemaNode(colander.String(), missing='')
    keyword = colander.SchemaNode(colander.String(), missing='')
    tags = colander.SchemaNode(colander.String(), missing='') # タグマスタと紐付ける用。ajaxで書いたほうがいいかも

    layout_id = colander.SchemaNode(colander.Integer())
    structure = colander.SchemaNode(colander.String(), validator=json_validator,
        widget=deform.widget.TextAreaWidget())

PageAddForm = Form(PageSchema(), buttons=('submit',), use_ajax=True)
PageEditForm = Form(PageSchema(), buttons=('submit', 'duplicate'), use_ajax=True)
