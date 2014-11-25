from wtforms.widgets.core import HTMLString
from .input import OurTextInput

__all__ = [
    'PercentageInput',
    ]

class PercentageInput(OurTextInput):
    def __call__(self, field, **kwargs):
        rendrant = super(PercentageInput, self).__init__(field, **kwargs)
        rendrant.html += u'%'
        return rendrant
