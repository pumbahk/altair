# -*- coding:utf-8 -*-
import wtforms.form as form
import wtforms.ext.sqlalchemy.fields as extfields

from altaircms.topic.models import Topic

def existing_topics():
    ##本当は、client.id, site.idでfilteringする必要がある
    ##本当は、日付などでfilteringする必要がある
    return Topic.query.all()

class TopicChoiceForm(form.Form):
    topic = extfields.QuerySelectField(id="select_topic", label=u"", query_factory=existing_topics, allow_blank=False)
