# coding: utf-8

from altaircms.formhelpers import Form

from wtforms import fields, validators

from altaircms.formhelpers import required_field, append_errors
from altaircms.formhelpers import dynamic_query_select_field_factory

from ..models import Word, WordSearch

from altaircms.event.forms import getLabelFromWord

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


def wordFormQueryFactory(model, request, allowable):
    q = allowable.filter(Word.deleted_at==None).order_by(Word.label_kana)\
        .filter(Word.merge_to_word_id==None)
    if 'id' in request.matchdict:
        q = q.filter(Word.id != request.matchdict['id'])
    return q


class WordForm(Form):
    merge_to_word = dynamic_query_select_field_factory(
        Word, allow_blank=True, label=u"統合先 お気に入りワード",
        multiple=False,
        dynamic_query=wordFormQueryFactory, break_separate=False,
        get_label=getLabelFromWord)
    label = fields.TextField(label=u'見出し', validators=[required_field()])
    label_kana = fields.TextField(label=u'見出しヨミガナ', validators=[required_field()])
    # TODO: カタカナvalidation
    type = fields.SelectField(label=u'種別', choices=choices, default=choices[0], validators=[required_field()])
    word_searches = TextListField(label=u'別名', model=WordSearch)
    description = fields.TextAreaField(label=u'説明')

    def configure(self, request):
        self.request = request

        mergeable = False
        if "id" in self.request.matchdict and self.request.matchdict["id"] is not None:
            logger.info("id=%s" % repr(self.request.matchdict["id"]))
            merge_from_words = self.request.allowable(Word).filter(Word.deleted_at==None)\
                    .filter_by(merge_to_word_id=int(self.request.matchdict["id"])).all()
            if len(merge_from_words) == 0:
                mergeable = True

        if mergeable:
            self.__display_fields__ = ["label", "label_kana", "type", "word_searches", "description", "merge_to_word"]
        else:
            self.__display_fields__ = ["label", "label_kana", "type", "word_searches", "description"]

    def object_validate(self, obj=None):
        data = self.data

        qs = self.request.allowable(Word).filter_by(label=data["label"])
        if obj is not None:
            qs = qs.filter(Word.id!=obj.id)
        if qs.count() > 0:
            append_errors(self.errors, "label", u'"%s" は既に登録されてます' % data["label"])
            return False

        if obj is not None:
            merge_words = self.request.allowable(Word).filter(Word.deleted_at==None).filter_by(merge_to_word_id=obj.id).all()
            if 0 < len(merge_words):
                if "merge_to_word" in data and data["merge_to_word"] is not None:
                    logger.warning("multi level merge is not supported.")
                    append_errors(self.errors, "merge_to_word", u'統合先のワードをさらに別のワードへの統合できません')
                    return False

        if "merge_to_word" in data and data["merge_to_word"]:
            qs = self.request.allowable(Word).filter_by(id=data["merge_to_word"].id)
            parents = qs.all()
            if len(parents) == 0:
                append_errors(self.errors, "merge_to_word", u'指定されたIDのお気に入りワードが見つかりません')
                return False

        return True
