# -*- coding:utf-8 -*-
import itertools
import wtforms.form as form
import wtforms.fields as fields
import wtforms.validators as validators
from altaircms.topic.models import Topic
from altaircms.topic.models import Topcontent
from altaircms.models import DBSession
from altaircms.plugins.api import get_extra_resource

"""
レンダリングされるtopicモデルの種類
----------------------------------------

noimage(文章のみ)では、topic modelが
hasimage(画像あり)では、topcontentがレンダリングされる
"""

class TopicChoiceForm(form.Form):
    DISC_CHOICES = [("noimage", u"文章のみ"), ("hasimage", u"画像あり")]
    topic_type = fields.SelectField(id="topic_type", label=u"表示形式", choices=DISC_CHOICES) #todo rename

    kind = fields.SelectField(id="kind", label=u"表示するトピックの種類", choices=[])
    subkind = fields.SelectField(id="subkind", label=u"サブ分類")
    display_count = fields.IntegerField(id="display_count", label=u"表示件数", default=5, validators=[validators.Required()])
    display_global = fields.BooleanField(id="display_global", label=u"グローバルトピックを表示", default=True)
    display_page = fields.BooleanField(id="display_page", label=u"このページに紐つけられたトピックだけを表示", default=True)
    display_event = fields.BooleanField(id="display_event", label=u"このイベントに紐つけられたトピックだけを表示", default=True)

    def configure(self, request):
        ## todo まじめに分離
        extra_resource = get_extra_resource(request)
        self.kind.choices = [(x, x) for x in extra_resource["topic_kinds"]] + [(x, x) for x in extra_resource["topcontent_kinds"]] 

        qs0 = Topic.query.filter(Topic.kind.in_(extra_resource["topic_kinds"]))
        qs0 = qs0.with_entities("subkind").group_by("subkind")
        qs1 = Topcontent.query.filter(Topcontent.kind.in_(extra_resource["topcontent_kinds"]))
        qs1 = qs1.with_entities("subkind").group_by("subkind")
        self.subkind.choices = [(q[0], q[0]) for q in itertools.chain(qs0, qs1)]
