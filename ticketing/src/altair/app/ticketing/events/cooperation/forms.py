#-*- coding: utf-8 -*-
from wtforms import (
    Form,
    SubmitField,    
    SelectField,
    SelectMultipleField,
    )
from wtforms.validators import (
    Required,
    )
from wtforms.widgets import (
    CheckboxInput,
    ListWidget,
    )
from altair.app.ticketing.core.models import (
    StockHolder,
    )
from .errors import PutbackFormCreateError


class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

class PutbackForm(Form):
    stock_holder_id = SelectField(
        label=u'枠',
        validators=[Required()],
        choices=[],
        coerce=int,
    )
    performance_ids = MultiCheckboxField(
        label=u'パフォーマンス',
        validators=[Required()],
        choices=[],
    )

    submit = SubmitField(
        label=u'返券する',
    )

    def __init__(self, formdata=None, obj=None, prefix='', **kwds):
        super(PutbackForm, self).__init__(formdata, obj, prefix, **kwds)
        event = kwds.get('event')
        if not event:
            raise PutbackFormCreateError()
        self.stock_holder_id.choices = [
            (stock_holder.id, stock_holder.name)
            for stock_holder in event.stock_holders
            ]
        self.performance_ids.choices = [
            (performance.id, performance.name)
            for performance in event.performances
            ]
