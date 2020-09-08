# -*- coding: utf-8 -*-
from altair.formhelpers import after1900
from altair.formhelpers.fields import DateTimeField, OurTextField, OurTextAreaField, OurSelectField, OurRadioField
from altair.formhelpers.form import OurForm
from wtforms.validators import Optional, Required
from standardenum import StandardEnum


class TemplateTypeEnum(StandardEnum):
    Normal = 1
    Vimeo = 2
    VimeoWithChat = 3


class PublicFlagType(StandardEnum):
    OFF = 0
    ON = 1


class LiveStreamingForm(OurForm):

    public_flag = OurRadioField(
        label=u'Live_Streaming連携',
        choices=[
            (int(PublicFlagType.OFF), u'OFF'),
            (int(PublicFlagType.ON), u'ON')],
        default=PublicFlagType.OFF,
        coerce=int
    )

    template_type = OurSelectField(
        label=u'テンプレート種別',
        validators=[Required()],
        choices=[
            (int(TemplateTypeEnum.Normal), u'汎用テンプレート'),
            (int(TemplateTypeEnum.Vimeo), u'Vimeoチャット無し'),
            (int(TemplateTypeEnum.VimeoWithChat), u'Vimeoチャット有り'),
                 ],
        default=TemplateTypeEnum.Normal,
        coerce=int
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


