# coding: utf-8
import re
from wtforms import form, fields, validators
from altaircms.interfaces import IForm
from altaircms.interfaces import implementer


class OnlyExtsFileGen(object):
    def __init__(self, exts, fmt=None):
        self.exts = exts
        self.fmt = "invalid file type: fielname=%s [support format is %s]"


    def __call__(self, form, field):
        if field.data == "":
            raise validators.ValidationError("%s file not found" % form.type)

        fname = field.data.filename
        if not any(fname.endswith(ext) for ext in self.exts):
            raise validators.ValidationError(self.fmt % (fname, self.exts))
        
    def none_is_ok(self, form, field):
        if not field.data:
            return None
        else:
            return self.__call__(form, field)


def validate_filepath(form, field):
    if field.data:
        field.data.filename = re.sub(r'[^a-z0-9_.-]', '_', field.data.filename)


only_image_file = OnlyExtsFileGen((".jpg", ".jpeg", ".png", ".gif"))
@implementer(IForm)
class ImageAssetForm(form.Form):
    type = "image"
    alt = fields.TextField(default='')
    filepath = fields.FileField(label=u'画像を投稿', 
                                validators=[only_image_file, validate_filepath])
    tags = fields.TextField(label=u"タグ")
    private_tags = fields.TextField(label=u"非公開タグ")


@implementer(IForm)
class ImageAssetUpdateForm(form.Form):
    type = "image"
    alt = fields.TextField(default='')
    filepath = fields.FileField(label=u'画像を投稿(空欄の場合には以前の画像がそのまま使われます)',
                                validators=[only_image_file.none_is_ok, validate_filepath])
    tags = fields.TextField(label=u"タグ")
    private_tags = fields.TextField(label=u"非公開タグ")


only_movie_file = OnlyExtsFileGen((".mov", ".mp4"))
@implementer(IForm)
class MovieAssetForm(form.Form):
    type = "movie"
    alt = fields.TextField(default='')
    filepath = fields.FileField(label=u'動画を投稿',
                                validators=[only_movie_file, validate_filepath])
    placeholder = fields.FileField(label=u'プレースホルダー(空欄の場合にはダミーの画像が使われます)',
                                   validators=[only_image_file.none_is_ok, validate_filepath])
    tags = fields.TextField(label=u"タグ")
    private_tags = fields.TextField(label=u"非公開タグ")


@implementer(IForm)
class MovieAssetForm(form.Form):
    type = "movie"
    alt = fields.TextField(default='')
    filepath = fields.FileField(label=u'動画を投稿',
                                validators=[only_movie_file, validate_filepath])
    placeholder = fields.FileField(label=u'プレースホルダー(空欄の場合にはダミーの画像が使われます)',
                                   validators=[only_image_file.none_is_ok, validate_filepath])
    tags = fields.TextField(label=u"タグ")
    private_tags = fields.TextField(label=u"非公開タグ")


@implementer(IForm)
class MovieAssetUpdateForm(form.Form):
    type = "movie"
    alt = fields.TextField(default='')
    filepath = fields.FileField(label=u'動画を投稿(空欄の場合には以前の画像がそのまま使われます)',
                                validators=[only_movie_file.none_is_ok, validate_filepath])
    placeholder = fields.FileField(label=u'プレースホルダー(空欄の場合にはダミーの画像が使われます)',
                                   validators=[only_image_file.none_is_ok, validate_filepath])
    tags = fields.TextField(label=u"タグ")
    private_tags = fields.TextField(label=u"非公開タグ")


only_flash_file = OnlyExtsFileGen((".swf", ))
@implementer(IForm)
class FlashAssetForm(form.Form):
    type = "flash"
    alt = fields.TextField(default='')
    filepath = fields.FileField(label=u'flashを投稿',
                                validators=[only_flash_file, validate_filepath])
    placeholder = fields.FileField(label=u'プレースホルダー(空欄の場合にはダミーの画像が使われます)', 
                                   validators=[only_image_file.none_is_ok, validate_filepath])
    tags = fields.TextField(label=u"タグ")
    private_tags = fields.TextField(label=u"非公開タグ")


@implementer(IForm)
class FlashAssetUpdateForm(form.Form):
    type = "flash"
    alt = fields.TextField(default='')
    filepath = fields.FileField(label=u'flashを投稿(空欄の場合には以前の画像がそのまま使われます)',
                                validators=[only_flash_file.none_is_ok, validate_filepath])
    placeholder = fields.FileField(label=u'プレースホルダー(空欄の場合にはダミーの画像が使われます)', 
                                   validators=[only_image_file.none_is_ok, validate_filepath])
    tags = fields.TextField(label=u"タグ")
    private_tags = fields.TextField(label=u"非公開タグ")


@implementer(IForm)
class NoValidAssetForm(form.Form):
    type = "image" # default
    alt = fields.TextField(default='')
    filepath = fields.FileField(label='upload file')
    tags = fields.TextField(label=u"タグ")
    private_tags = fields.TextField(label=u"非公開タグ")
    
def get_confirm_asset_form_by_asset_type(asset_type=None):
    if asset_type == "image":
        return ImageAssetForm
    elif asset_type == "movie":
        return MovieAssetForm
    elif asset_type == "flash":
        return FlashAssetForm
    raise Exception("asset type %s is not supported")
