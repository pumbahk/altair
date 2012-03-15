# coding: utf-8
import json
from wtforms.form import Form
from wtforms import fields
from wtforms import widgets
import wtforms.ext.sqlalchemy.fields as extfields
from altaircms.layout.models import Layout

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
-    keywords = colander.SchemaNode(colander.String(), missing='')
-    tags = colander.SchemaNode(colander.String(), missing='') # タグマスタと紐付ける用。ajaxで書いたほうがいいかも
-
-    layout_id = colander.SchemaNode(colander.Integer())
-    # structure = colander.SchemaNode(colander.String(), validator=json_validator,
-    #                                 widget=deform.widget.TextAreaWidget())
"""


def existing_layouts():
    ##本当は、client.id, site.idでfilteringする必要がある
    ##本当は、日付などでfilteringする必要がある
    return Layout.query.all()

class PageForm(Form):
    url = fields.TextField()
    title = fields.TextField()
    description = fields.TextField()
    keywords = fields.TextField()
    tags = fields.TextField()
    layout = extfields.QuerySelectField(query_factory=existing_layouts, allow_blank=False)
    event_id = fields.IntegerField(label=u"", widget=widgets.HiddenInput())
