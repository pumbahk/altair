# coding: utf-8
import colander
import deform
from deform.form import Form
from deform.interfaces import FileUploadTempStore

__all__ = [
    'ASSET_TYPE',
    'ImageAssetForm',
    'MovieAssetForm',
    'FlashAssetForm',
]

ASSET_TYPE = [
    'image',
    'movie',
    'flash',
]

tmpstore = FileUploadTempStore()


class Asset(colander.MappingSchema):
    type = colander.SchemaNode(colander.String())


class ImageAsset(Asset):
    alt = colander.SchemaNode(colander.String(), missing=colander.null, default='')
    width = colander.SchemaNode(colander.Integer())
    height = colander.SchemaNode(colander.Integer())
    image = colander.SchemaNode(
        deform.FileData(),
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


ImageAssetForm = Form(ImageAsset(), buttons=('submit',), use_ajax=True)
MovieAssetForm = Form(MovieAsset(), buttons=('submit',), use_ajax=True)
FlashAssetForm = Form(FlashAsset(), buttons=('submit',), use_ajax=True)
