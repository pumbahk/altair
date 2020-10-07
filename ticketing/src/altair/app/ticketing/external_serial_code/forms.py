# -*- coding: utf-8 -*-

import logging
from altair.app.ticketing import csvutils as csv

from altair.formhelpers import Required, JISX0208, after1900
from altair.formhelpers.fields import OurDateTimeField, OurTextField, OurTextAreaField, \
    OurHiddenField
from altair.formhelpers.form import OurForm
from wtforms.fields import FileField
from wtforms.validators import Length, Optional, URL, ValidationError

logger = logging.getLogger(__name__)


class ExternalSerialCodeSettingSearchForm(OurForm):
    name = OurTextField(
        label=u'名前',
        validators=[
            Required(),
            JISX0208,
            Length(max=200, message=u'200文字以内で入力してください'),
        ]
    )


class ExternalSerialCodeSearchForm(OurForm):
    search_word = OurTextField(
        label=u'検索文字列',
        validators=[
            Required(),
            JISX0208,
            Length(max=200, message=u'200文字以内で入力してください'),
        ]
    )


class ExternalSerialCodeSettingEditForm(OurForm):
    id = OurHiddenField(
        label=u'ID',
        validators=[Optional()],
    )
    name = OurTextField(
        label=u'名前',
        validators=[
            Required(),
            JISX0208,
            Length(max=200, message=u'200文字以内で入力してください'),
        ]
    )
    label = OurTextField(
        label=u'購入履歴表示名',
        validators=[
            Required(),
            JISX0208,
            Length(max=200, message=u'200文字以内で入力してください'),
        ]
    )
    description = OurTextAreaField(
        label=u'説明',
        validators=[Optional()],
    )
    url = OurTextField(
        label=u'URL',
        validators=[
            Optional(),
            URL(message=u"URL形式で入力してください"),
            Length(max=200, message=u'200文字以内で入力してください'),
        ]
    )
    start_at = OurDateTimeField(
        label=u'開始日時',
        validators=[Required(), after1900],
        format='%Y-%m-%d %H:%M',
    )
    end_at = OurDateTimeField(
        label=u'終了日時',
        validators=[Required(), after1900],
        format='%Y-%m-%d %H:%M',
    )


class UploadForm(OurForm):

    upload_file = FileField(
        label=u'ファイル'
    )

    def validate(self):
        super(UploadForm, self).validate()
        if not hasattr(self.data["upload_file"], "file"):
            self.upload_file.errors = self.errors[
                "upload_file"] = [u"csvファイルを指定してください。"]
            return not bool(self.errors)

        io = self.data["upload_file"].file
        try:
            reader = csv.reader(
                io, quotechar="'", encoding="shift_jis")
            for code_1_name, code_1, code_2_name, code_2 in reader:
                pass
        except UnicodeDecodeError as e:
            logger.info("*csv import* %s" % (str(e)))
            self.upload_file.errors = self.errors["upload_file"] = [
                u"csvファイルが壊れています。あるいは指定しているエンコーディングが異なっているかもしません。"]
        except Exception as e:
            logger.info(e.__class__)
            logger.info("*csv import* %s" % (str(e)))
            self.upload_file.errors = self.errors["upload_file"] = [u"csvファイルが壊れています。"]
        io.seek(0)
        return not bool(self.errors)
