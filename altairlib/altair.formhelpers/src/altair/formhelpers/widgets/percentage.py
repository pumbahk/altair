from wtforms.widgets.core import HTMLString
from .input import OurTextInput

__all__ = [
    'PercentageInput',
    ]

class PercentageInput(OurTextInput):
    def _render_suffix(self, field, **kwargs):
        return u'%'
