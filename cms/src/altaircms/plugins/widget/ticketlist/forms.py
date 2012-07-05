# -*- coding:utf-8 -*-
import wtforms.form as form
import wtforms.fields as fields
import wtforms.widgets as widgets
import wtforms.ext.sqlalchemy.fields as extfields

import wtforms.validators as validators
from altaircms.models import Performance
from altaircms.models import Sale
from altaircms.seeds.saleskind import SALESKIND_CHOICES

class TicketlistChoiceForm(form.Form):
    ## todo fix
    kind = fields.SelectField(id="kind", label=u"表示するチケットの種別", choices=SALESKIND_CHOICES)
    target_performance = extfields.QuerySelectField(id="target", label=u"価格表を取得するパフォーマンス", 
                                                    query_factory= lambda : Performance.query, 
                                                    get_label= lambda obj : u"%s(日時:%s, 場所:%s)" % (obj.title, obj.start_on, obj.venue))
    caption = fields.TextField(id="caption", label=u"価格表の見出し", widget=widgets.TextArea())
    def refine_choices(self, request, page_id):
        if not page_id:
            return

        ## pageで絞り込んでいるから大丈夫なはず。organization的に
        page = request.allowable("Page").filter_by(id=page_id).first()
        if page is None:
            return
        ## sales choice
        qs = Sale.query.filter(Sale.event_id==page.event_id)
        self.kind.choices = [(s.kind, s.jkind) for s in set(qs)]

        ## performance choice
        qs = Performance.query.filter(Performance.event_id==page.event_id)
        self.target_performance.choices = qs
        self.target_performance.query_factory = lambda : qs
