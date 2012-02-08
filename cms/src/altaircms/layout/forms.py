# coding: utf-8
import colander

class LayoutSchema(colander.Schema):
    title = colander.SchemaNode(colander.String(), missing=colander.null)
    template_filename = colander.SchemaNode(colander.String())
