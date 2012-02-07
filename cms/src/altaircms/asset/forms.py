# coding: utf-8
import colander
import deform

__all__ = [
    'ASSET_TYPE',
    'ImageAssetSchema',
    'MovieAssetSchema',
    'FlashAssetSchema',
    'CssAssetSchema',
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


class BaseAssetSchema(colander.MappingSchema):
    type = colander.SchemaNode(
        colander.String(),
        validator=colander.OneOf(ASSET_TYPE),
        widget=deform.widget.HiddenWidget()
    )


#@TODO: 画像フォーマットやサイズのバリデーションを行う
class ImageAssetSchema(BaseAssetSchema):
    alt = colander.SchemaNode(colander.String(), missing=colander.null, default='')
    width = colander.SchemaNode(colander.Integer(), missing=colander.null)
    height = colander.SchemaNode(colander.Integer(), missing=colander.null)
    uploadfile = colander.SchemaNode(
        deform.schema.FileData(),
        title='画像ファイル',
        widget=deform.widget.FileUploadWidget(tmpstore)
    )


class FlashAssetSchema(BaseAssetSchema):
    width = colander.SchemaNode(colander.Integer(), missing=colander.null)
    height = colander.SchemaNode(colander.Integer(), missing=colander.null)
    length = colander.SchemaNode(colander.Integer(), missing=colander.null)
    uploadfile = colander.SchemaNode(
        deform.FileData(),
        title='Flashファイル',
        widget=deform.widget.FileUploadWidget(tmpstore)
    )


class MovieAssetSchema(BaseAssetSchema):
    width = colander.SchemaNode(colander.Integer(), missing=colander.null)
    height = colander.SchemaNode(colander.Integer(), missing=colander.null)
    length = colander.SchemaNode(colander.Integer(), missing=colander.null)
#    mimetype = colander.SchemaNode(colander.String(), missing=colander.null)
    uploadfile = colander.SchemaNode(
        deform.FileData(),
        title='動画ファイル',
        widget=deform.widget.FileUploadWidget(tmpstore)
    )


class CssAssetSchema(BaseAssetSchema):
    pass
