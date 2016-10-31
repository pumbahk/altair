# -*- coding:utf-8 -*-
import logging
from wtforms import Form
from wtforms import fields
from wtforms import ValidationError

logger = logging.getLogger(__name__)


class ImageUploadForm(Form):
    upload_file = fields.FileField(label=u"imageファイル")

    def validate_upload_file(form, field):
        if not field.data.filename.endswith('png'):
            raise ValidationError(u"pngファイルのみアップロード可能です。")

    """
    def validate(self):
        super(ImageUploadForm, self).validate()
        if not hasattr(self.data["upload_file"], "file"):
            self.csvfile.errors = self.errors[
                "upload_file"] = [u"指定してください。"]
            return not bool(self.errors)
    """
