# coding: utf-8
import json
from wtforms.form import Form
from wtforms import fields

"""
def json_validator(node, value):
    try:
        json.loads(value)
    except ValueError:
        raise colander.Invalid(node, 'JSON object required')
"""

"""

-class PageSchema(colander.MappingSchema):
-    url = colander.SchemaNode(colander.String())
-    title = colander.SchemaNode(colander.String())
-    description = colander.SchemaNode(colander.String(), missing='')
-    keyword = colander.SchemaNode(colander.String(), missing='')
-    tags = colander.SchemaNode(colander.String(), missing='') # タグマスタと紐付ける用。ajaxで書いたほうがいいかも
-
-    layout_id = colander.SchemaNode(colander.Integer())
-    # structure = colander.SchemaNode(colander.String(), validator=json_validator,
-    #                                 widget=deform.widget.TextAreaWidget())
"""


class PageForm(Form):
    url = fields.TextField()
    title = fields.TextField()
    description = fields.TextField()
    keyword = fields.TextField()
    tags = fields.TextField()
    layout_id = fields.SelectField(coerce=int)
    structure = fields.TextField()
