# -*- coding: utf-8 -*-
from wtforms.validators import Optional
from altair.formhelpers import after1900
from altair.formhelpers.form import OurForm
from altair.formhelpers.fields import OurSelectField, DateTimeField, OurTextField, OurTextAreaField
from altair.app.ticketing.core.models import (
    ProductItem
)


class LiveStreamingForm(OurForm):

    label = OurTextField(
        label=u"ラベル",
        note=u"ラベル",
    )
    live_code = OurTextAreaField(
        label=u"連携コード",
        note=u"連携コード",
    )
    description = OurTextAreaField(
        label=u"説明文",
        note=u"説明文",
    )
    publish_start_at = DateTimeField(
        label=u'開始時間',
        validators=[Optional(), after1900],
        format='%Y-%m-%d %H:%M',
    )
    publish_end_at = DateTimeField(
        label=u'終了時間',
        validators=[Optional(), after1900],
        format='%Y-%m-%d %H:%M',
    )
