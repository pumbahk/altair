# -*- coding: utf-8 -*-

from wtforms.form import Form
from wtforms import fields
from wtforms import validators
from altair.formhelpers import Translations
from altair.app.ticketing.core.models import Order, Performance
from . import helpers as h

            
class MiscOrderFindForm(Form):
    order_no = fields.TextField(u"注文番号", validators=[validators.Required()])

    def object_validate(self, organization_id):
        order_no = self.data["order_no"]
        order = Order.query.filter_by(organization_id=organization_id, order_no=order_no).first()
        if order is None:
            self.order_no.errors.append(u'注文が見つかりません。')
            return False

        self.order = order
        return True

def _performance_describe(p):
    return u"%s  (%s)" % (p.name, h.japanese_datetime(p.start_on))

class PerformanceSelectForm(Form):
    def __init__(self, formdata=None, obj=None, prefix='',event_id=None,  **kwargs):
        Form.__init__(self, formdata, obj, prefix, **kwargs)
        if event_id:
            qs = Performance.query.filter_by(event_id=event_id)
            self.performance_id.choices = [(unicode(p.id), _performance_describe(p)) for p in qs]
        if obj:
            self.performance_id.data = unicode(obj.id)

    def _get_translations(self):
        return Translations()

    performance_id = fields.SelectField(
        label=u"公演", 
        choices=[], 
        coerce=unicode, 
        )


    
