# -*- coding:utf-8 -*-
import logging
from wtforms import Form
from wtforms import fields
from wtforms import ValidationError

logger = logging.getLogger(__name__)


class ImageUploadForm(Form):
    upload_file = fields.FileField(label=u"imageファイル")

    def validate_upload_file(form, field):
        if not hasattr(field.data, "filename"):
            raise ValidationError(u"ファイルを指定してください")
        if not (field.data.filename.endswith('png') or field.data.filename.endswith('jpg')):
            raise ValidationError(u"jpg/pngファイルのみアップロード可能です。")
