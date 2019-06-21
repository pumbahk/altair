# coding: utf-8

import logging
import unicodedata

from altaircms.formhelpers import Form
from altaircms.formhelpers import required_field
from wtforms import ValidationError
from wtforms import fields

logger = logging.getLogger(__file__)


class ArtistEditForm(Form):
    id = fields.TextField(label=u'アーティストID')
    name = fields.TextField(label=u'アーティスト名', validators=[required_field()])
    kana = fields.TextField(label=u'アーティスト名カナ', validators=[required_field()])
    code = fields.TextField(label=u'コード')
    url = fields.TextField(label=u'URL')
    image = fields.TextField(label=u'画像パス', validators=[required_field()])
    description = fields.TextAreaField(label=u'説明')
    public = fields.BooleanField(label=u'公開／非公開', default=True)

    def validate_kana(self, field):
        for ch in field.data:
            try:
                name = unicodedata.name(unicode(ch))
                if not name.count("KATAKANA"):
                    raise ValidationError(u"カタカナを入力してください")
            except (UnicodeDecodeError, TypeError):
                raise ValidationError(u"カタカナを入力してください")
