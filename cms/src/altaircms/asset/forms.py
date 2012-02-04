# coding: utf-8
import colander
import deform

__all__ = [
    'ASSET_TYPE',
    'ImageAsset',
    'MovieAsset',
    'FlashAsset',
    'CssAsset',
]

ASSET_TYPE = [
    'image',
    'movie',
    'flash',
]

class Store(dict):
    def preview_url(self, name):
        return None

tmpstore = Store()


class Asset(colander.MappingSchema):
    type = colander.SchemaNode(
        colander.String(),
        validator=colander.OneOf(ASSET_TYPE),
        widget=deform.widget.HiddenWidget()
    )


class ImageAsset(Asset):
    alt = colander.SchemaNode(colander.String(), missing=colander.null, default='')
    width = colander.SchemaNode(colander.Integer(), missing=colander.null)
    height = colander.SchemaNode(colander.Integer(), missing=colander.null)
    image = colander.SchemaNode(
        deform.schema.FileData(),
        widget=deform.widget.FileUploadWidget(tmpstore)
    )


class FlashAsset(Asset):
    width = colander.SchemaNode(colander.Integer())
    height = colander.SchemaNode(colander.Integer())
    length = colander.SchemaNode(colander.Integer())
    flash = colander.SchemaNode(
        deform.FileData(),
        widget=deform.widget.FileUploadWidget(tmpstore)
    )


class MovieAsset(Asset):
    width = colander.SchemaNode(colander.Integer())
    height = colander.SchemaNode(colander.Integer())
    length = colander.SchemaNode(colander.Integer())
    mimetype = colander.SchemaNode(colander.String())
    movie = colander.SchemaNode(
        deform.FileData(),
        widget=deform.widget.FileUploadWidget(tmpstore)
    )


class CssAsset(Asset):
    pass
