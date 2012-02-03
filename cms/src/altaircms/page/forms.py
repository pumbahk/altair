# coding: utf-8
import json

import colander
from deform.form import Form


def json_validator(node, value):
    try:
        json.loads(value)
    except ValueError:
        raise colander.Invalid(node, 'JSON object required')


class PageMetadataSchema(colander.MappingSchema):
    url = colander.SchemaNode(colander.String())
    title = colander.SchemaNode(colander.String())
    description = colander.SchemaNode(colander.String())
    keyword = colander.SchemaNode(colander.String())
    tags = colander.SchemaNode(colander.String())


class PageSchema(colander.MappingSchema):
    layout_id = colander.SchemaNode(colander.Integer())
    structure = colander.SchemaNode(colander.String(), validator=json_validator)


PageMetadataEditForm = Form(PageMetadataSchema(), buttons=('submit',), use_ajax=True)
PageEditForm = Form(PageSchema(), buttons=('submit',), use_ajax=True)
