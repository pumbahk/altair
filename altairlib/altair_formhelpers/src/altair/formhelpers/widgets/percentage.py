from wtforms.widgets.core import HTMLString, TextInput

__all__ = [
    'PercentageInput',
    ]

class PercentageInput(TextInput):
    def __call__(self, field, **kwargs):
        return HTMLString(
            super(self.__class__, self).__call__(field, **kwargs) +
            '%'
            )

