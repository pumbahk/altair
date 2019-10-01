# coding: utf-8

import logging
import unicodedata

from altaircms.formhelpers import Form
from altaircms.formhelpers import required_field
from altair.formhelpers import DateTimeField, Translations, Required
from wtforms import ValidationError
from wtforms import fields,validators

logger = logging.getLogger(__file__)


class ArtistEditForm(Form):
    id = fields.TextField(label=u'アーティストID')
    name = fields.TextField(label=u'アーティスト名', validators=[required_field()])
    kana = fields.TextField(label=u'アーティスト名カナ', validators=[required_field()])
    code = fields.TextField(label=u'コード')
    url = fields.TextField(label=u'URL')
    image = fields.TextField(label=u'画像パス', validators=[required_field()])
    description = fields.TextAreaField(label=u'説明')
    twitter = fields.TextField(label=u'ツイッター')
    facebook = fields.TextField(label=u'Facebook')
    line = fields.TextField(label=u'LINE')
    instagram = fields.TextField(label=u'インスタグラム')
    official = fields.TextField(label=u'オフィシャルページ')
    funclub = fields.TextField(label=u'ファンクラブ')
    public = fields.BooleanField(label=u'公開／非公開', default=True)

    def validate_kana(self, field):
        for ch in field.data:
            try:
                name = unicodedata.name(unicode(ch))
                if not name.count("KATAKANA"):
                    raise ValidationError(u"カタカナを入力してください")
            except (UnicodeDecodeError, TypeError, ValueError):
                raise ValidationError(u"カタカナを入力してください")


class ArtistLinkForm(Form):
    def __init__(self, *args, **kw):
        Form.__init__(self, *args, **kw)
        if kw:
            artists = kw['formdata']['artists']

            artists_choices = [(artist.id, artist.name) for artist in artists]
            self.artist.choices = [(0, u'')]
            self.artist.choices.extend(artists_choices)

    event_id = fields.HiddenField(label=u'イベントID')
    artist = fields.SelectField(
        label=u'',
        coerce=int
    )


class NowSettingForm(Form):
    def _get_translations(self):
        return Translations()

    now = DateTimeField(label=u"現在時刻", validators=[Required()])
    redirect_to = fields.TextField(label=u"リダイレクト先", validators=[validators.Optional(), validators.URL])
