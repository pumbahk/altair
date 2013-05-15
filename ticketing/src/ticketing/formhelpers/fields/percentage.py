from wtforms import fields
from ..fields import OurField
from ..widgets import PercentageInput
from .core import _gen_field_init, RendererMixin

__all__ = [
    'PercentageField',
    ]

class PercentageField(OurField):
    widget = PercentageInput()
    precision = 2

    def __init__(self, *args, **kwargs):
        precision = kwargs.pop('precision', None)
        super(PercentageField, self).__init__(*args, **kwargs)
        if precision is not None:
            self.precision = precision

    def process_formdata(self, valuelist):
        if valuelist:
            try:
                self.data = float(valuelist[0]) / 100.
            except ValueError:
                self.data = None
                raise ValueError(self.gettext('Not a valid float value'))

    def _format(self, data):
        return (u"%%.%df" % self.precision) % data

    def _value(self):
        if self.raw_data:
            return self.raw_data[0]
        elif self.data is not None:
            return self._format(self.data * 100)
        else:
            return u''
