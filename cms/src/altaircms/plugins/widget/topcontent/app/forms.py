# -*- coding:utf-8 -*-
import wtforms.form as form
import wtforms.ext.sqlalchemy.fields as extfields

from altaircms.topic.models import Topcontent

def existing_topcontents():
    ##本当は、client.id, organization.idでfilteringする必要がある
    ##本当は、日付などでfilteringする必要がある
    return Topcontent.query.all()

class TopcontentChoiceForm(form.Form):
    topcontent = extfields.QuerySelectField(label=u"トピック", query_factory=existing_topcontents, allow_blank=False)
