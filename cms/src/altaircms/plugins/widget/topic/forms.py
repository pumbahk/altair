# -*- coding:utf-8 -*-
import wtforms.form as form
import wtforms.fields as fields
import wtforms.validators as validators
from altaircms.topic.models import Topic
from altaircms.topcontent.models import Topcontent
from altaircms.models import DBSession

class TopicChoiceForm(form.Form):
    def configure_choices_field(self):
        choices = [(q[0], q[0])for q in DBSession.query(Topic.subkind).order_by("subkind").distinct()] ##
        self.subkind.choices = choices

    DISC_CHOICES = [("topic", u"文章のみ"), ("topcontent", u"トップコンテンツ")]
    topic_type = fields.SelectField(id="topic_type", label=u"discrminator", choices=DISC_CHOICES) #todo rename

    _choices = [(x, x) for x in Topic.KIND_CANDIDATES] + [(x, x) for x in Topcontent.KIND_CANDIDATES] 
    kind = fields.SelectField(id="kind", label=u"表示するトピックの種類", choices=_choices)
    subkind = fields.SelectField(id="subkind", label=u"サブ分類")
    display_count = fields.IntegerField(id="display_count", label=u"表示件数", default=5, validators=[validators.Required()])
    display_global = fields.BooleanField(id="display_global", label=u"グローバルトピックを表示", default=True)
    display_page = fields.BooleanField(id="display_page", label=u"ページに関連したトピック表示", default=True)
    display_event = fields.BooleanField(id="display_event", label=u"イベントに関連したトピック表示", default=True)

    # def transform(self, topic_type):
    #     if topic_type == "topcontent":
    #         self.kind.choices = [(x, x) for x in Topcontent.KIND_CANDIDATES]
    #     else:
    #         self.kind.choices = [(x, x) for x in Topic.KIND_CANDIDATES]
