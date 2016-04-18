# coding: utf-8

from altaircms.formhelpers import Form

from wtforms import fields, validators

from ..models import Word

from altaircms.formhelpers import required_field, append_errors
from altaircms.formhelpers import dynamic_query_select_field_factory

from pyramid.threadlocal import get_current_request

import logging
logger = logging.getLogger(__file__)

choices = [(u'artist', u'アーティスト'), (u'event', u'イベント'), (u'misc', u'その他')]

class WordForm(Form):
    label = fields.TextField(label=u'見出し', validators=[required_field()])
    label_kana = fields.TextField(label=u'見出しヨミガナ', validators=[required_field()])
    # TODO: カタカナvalidation
    type = fields.SelectField(label=u'種別', choices=choices, default=choices[0], validators=[required_field()])
    description = fields.TextAreaField(label=u'説明')

    __display_fields__ = [ "label", "label_kana", "type", "description" ]
