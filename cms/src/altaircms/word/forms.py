# coding: utf-8

from altaircms.formhelpers import Form

from wtforms import fields, validators

from altaircms.formhelpers import required_field, append_errors
from altaircms.formhelpers import dynamic_query_select_field_factory

from ..models import WordSearch

import logging
logger = logging.getLogger(__file__)

choices = [(u'artist', u'アーティスト'), (u'event', u'イベント'), (u'misc', u'その他')]

class TextListField(fields.TextAreaField):
    def __init__(self, model, **kwargs):
        super(TextListField, self).__init__(**kwargs)
        self._model = model

    def process_formdata(self, valuelist):
        if valuelist and isinstance(valuelist[0], basestring):
            self.data = [ self._model(_str=x) for x in valuelist[0].replace("\r", "").split("\n") if 0 < len(x) ]
        else:
            self.data = [ ]

    def _value(self):
        return u"\n".join(map(lambda x:unicode(x), self.data)) if self.data is not None else u""

class WordForm(Form):
    label = fields.TextField(label=u'見出し', validators=[required_field()])
    label_kana = fields.TextField(label=u'見出しヨミガナ', validators=[required_field()])
    # TODO: カタカナvalidation
    type = fields.SelectField(label=u'種別', choices=choices, default=choices[0], validators=[required_field()])
    word_searches = TextListField(label=u'別名', model=WordSearch)
    description = fields.TextAreaField(label=u'説明')

    __display_fields__ = [ "label", "label_kana", "type", "word_searches", "description" ]
