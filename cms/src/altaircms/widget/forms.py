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
    'MenuWidgetSchema',
    'BillinghistoryWidgetSchema',
    'TopicWidgetSchema',
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
    breadcrumb = colander.SchemaNode(colander.String(), widget=deform.widget.TextAreaWidget(), title=u'パンくず構造のJSONオブジェクト')


class MenuWidgetSchema(WidgetSchema):
    menu = colander.SchemaNode(colander.String(), widget=deform.widget.TextAreaWidget(), title=u'メニュー構造のJSONオブジェクト')


class BillinghistoryWidgetSchema(WidgetSchema):
    text = colander.SchemaNode(colander.String(), widget=deform.widget.TextAreaWidget(), title=u'購入履歴構造のJSONオブジェクト')


class TopicWidgetSchema(WidgetSchema):
    topic_id = colander.SchemaNode(colander.Integer(), title=u'トピックID')
    title = colander.SchemaNode(colander.String(), title=u'トピック名')


class ImageWidgetSchema(WidgetSchema):
    asset_id = colander.SchemaNode(colander.Integer())


class MovieWidgetSchema(WidgetSchema):
    asset_id = colander.SchemaNode(colander.Integer())


class FlashWidgetSchema(WidgetSchema):
    asset_id = colander.SchemaNode(colander.Integer())
