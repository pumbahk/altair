# coding: utf-8
import colander

class Event(colander.MappingSchema):
    title = colander.SchemaNode(colander.String())
    subtitle = colander.SchemaNode(colander.String(), missing=None)
    description = colander.SchemaNode(colander.String(), missing=None)
    place = colander.SchemaNode(colander.String(), missing=None)
    inquiry_for = colander.SchemaNode(colander.String(), missing='')
    event_open = colander.SchemaNode(colander.Date(), missing=None)
    event_close = colander.SchemaNode(colander.Date(), missing=None)
    deal_open = colander.SchemaNode(colander.Date(), missing=None)
    deal_close = colander.SchemaNode(colander.Date(), missing=None)
    is_searchable = colander.SchemaNode(colander.Integer(), missing=1, default=1)

event_schema = Event()
