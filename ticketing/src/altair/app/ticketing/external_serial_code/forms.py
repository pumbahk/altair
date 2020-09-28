# -*- coding: utf-8 -*-

import logging

from altair.formhelpers import Required, JISX0208, after1900
from altair.formhelpers.fields import OurDateTimeField, OurTextField, OurTextAreaField, \
    OurHiddenField
from altair.formhelpers.form import OurForm
from wtforms.validators import Length, Optional, URL

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
