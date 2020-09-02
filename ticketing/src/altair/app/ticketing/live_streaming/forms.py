# -*- coding: utf-8 -*-
from altair.formhelpers import after1900
from altair.formhelpers.fields import DateTimeField, OurTextField, OurTextAreaField, OurSelectField
from altair.formhelpers.form import OurForm
from wtforms.validators import Optional, Required
from standardenum import StandardEnum


class TemplateKindEnum(StandardEnum):
    Others = 1
    Vimeo = 2
    VimeowithChat = 3


class LiveStreamingForm(OurForm):
    template_status = OurSelectField(
        label=u'テンプレート種別',
        validators=[Required()],
        choices=[
            (TemplateKindEnum.Others, u'汎用テンプレート'),
            (TemplateKindEnum.Vimeo, u'Vimeoチャット無し'),
            (TemplateKindEnum.VimeowithChat, u'Vimeoチャット有り'),
                 ],
        coerce=int,
        help=u'''
              LivePerformanceのテンプレートを指定します。<br />
              ・汎用テンプレート<br />
              　Vimeo専用など
            '''
    )
    label = OurTextField(
        label=u"ラベル",
        note=u"ラベル",
    )
    artist_page = OurTextField(
        label=u"アーティストページ",
        note=u"アーティストページ",
    )
    live_code = OurTextAreaField(
        label=u"連携コード",
        note=u"連携コード",
    )
    live_chat_code = OurTextAreaField(
        label=u"チャット機能連携コード",
        note=u"チャット機能連携コード",
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


