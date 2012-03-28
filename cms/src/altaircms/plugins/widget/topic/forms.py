# -*- coding:utf-8 -*-
import wtforms.form as form
import wtforms.fields as fields
import wtforms.validators as validators
from altaircms.topic.models import Topic

class TopicChoiceForm(form.Form):
    kind = fields.SelectField(id="kind", label=u"トピックの種別", choices=[(x, x) for x in Topic.KIND_CANDIDATES])
    display_count = fields.IntegerField(id="display_count", label=u"表示件数", default=5, validators=[validators.Required()])
    display_global = fields.BooleanField(id="display_global", label=u"グローバルトピックを表示", default=True)
    display_page = fields.BooleanField(id="display_page", label=u"ページに関連したトピック表示", default=True)
    display_event = fields.BooleanField(id="display_event", label=u"イベントに関連したトピック表示", default=True)
    
