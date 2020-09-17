# -*- coding: utf-8 -*-

import logging

from altair.formhelpers import Required, JISX0208
from altair.formhelpers.fields import OurTextField
from altair.formhelpers.form import OurForm
from wtforms.validators import Length

logger = logging.getLogger(__name__)


class SearchForm(OurForm):
    label = OurTextField(
        label=u'ラベル検索文字列',
        validators=[
            Required(),
            JISX0208,
            Length(max=200, message=u'200文字以内で入力してください'),
        ]
    )
