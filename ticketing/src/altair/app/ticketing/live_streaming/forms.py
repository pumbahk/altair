# -*- coding: utf-8 -*-
from altair.formhelpers import after1900
from altair.formhelpers.fields import DateTimeField, OurTextField, OurTextAreaField
from altair.formhelpers.form import OurForm
from wtforms.validators import Optional, Required


class LiveStreamingForm(OurForm):
    label = OurTextField(
        label=u"ラベル",
        note=u"ラベル",
    )
    artist_page = OurTextField(
        label=u"イベント関連ページ",
        note=u"イベント関連ページ",
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
        validators=[Required(u"入力してください"), after1900],
        format='%Y-%m-%d %H:%M',
    )
    publish_end_at = DateTimeField(
        label=u'終了時間',
        validators=[Optional(), after1900],
        format='%Y-%m-%d %H:%M',
    )
