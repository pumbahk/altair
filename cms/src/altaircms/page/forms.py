# coding: utf-8
import colander
from deform.form import Form

class PageSchema(colander.MappingSchema):
    url = colander.SchemaNode(colander.String())
    title = colander.SchemaNode(colander.String())
    description = colander.SchemaNode(colander.String())
    keyword = colander.SchemaNode(colander.String())
    tags = colander.SchemaNode(colander.String())


PageEditForm = Form(PageSchema(), buttons=('submit',), use_ajax=True)
