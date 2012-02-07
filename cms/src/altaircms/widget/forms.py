# coding: utf-8
import colander
import deform

from altaircms.widget.models import WIDGET_TYPE

__all__ = [
    'TextWidgetSchema',
    'BreadcrumbsWidgetSchema',
    'ImageWidgetSchema',
    'MovieWidgetSchema',
    'FlashWidgetSchema',
]


class WidgetSchema(colander.Schema):
    type = colander.SchemaNode(
        colander.String(),
        validator=colander.OneOf(WIDGET_TYPE),
        widget=deform.widget.HiddenWidget()
    )


class TextWidgetSchema(WidgetSchema):
    title = colander.SchemaNode(colander.String())
    text = colander.SchemaNode(colander.String(), widget=deform.widget.TextAreaWidget())


class BreadcrumbsWidgetSchema(WidgetSchema):
    title = colander.SchemaNode(colander.String())
    text = colander.SchemaNode(colander.String(), widget=deform.widget.TextAreaWidget())


class ImageWidgetSchema(WidgetSchema):
    asset_id = colander.SchemaNode(colander.Integer())


class MovieWidgetSchema(WidgetSchema):
    asset_id = colander.SchemaNode(colander.Integer())


class FlashWidgetSchema(WidgetSchema):
    asset_id = colander.SchemaNode(colander.Integer())
