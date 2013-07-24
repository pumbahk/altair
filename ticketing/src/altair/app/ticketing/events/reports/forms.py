# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import SelectField

from altair.app.ticketing.core.models import StockHolder
from altair.formhelpers import Translations, Required

class ReportStockForm(Form):

    def _get_translations(self):
        return Translations()

    report_type = SelectField(
        label=u'明細タイプ',
        validators=[Required(u'選択してください')],
        choices=[
            ('stock', u'仕入明細'),
            ('unsold', u'残席明細'),
        ],
        coerce=str,
    )

class ReportByStockHolderForm(Form):

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata, obj, prefix, **kwargs)
        if 'event_id' in kwargs:
            self.stock_holder_id.choices = [
                (sh.id, sh.name) for sh in StockHolder.filter_by(event_id=kwargs['event_id']).all()
            ]

    def _get_translations(self):
        return Translations()

    stock_holder_id = SelectField(
        label=u'枠',
        validators=[Required(u'選択してください')],
        choices=[],
        coerce=int,
    )
    report_type = SelectField(
        label=u'明細タイプ',
        validators=[Required(u'選択してください')],
        choices=[
            ('assign', u'配券明細'),
            ('add', u'追券明細'),
            ('return', u'返券明細'),
            ('final_return', u'最終返券明細')
        ],
        coerce=str,
    )
