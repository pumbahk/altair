from wtforms.fields import StringField, SelectField
from wtforms.widgets import TextInput

__all__ = (
  'TextFieldWithChoice',
  )

class StringFieldWithChoice(StringField, SelectField):
    widget = TextInput()

    def _coerce(self, value):
        return self.coerce(value) if value is not None else ''

    def process_data(self, value):
        try:
            self.data = self._coerce(value)
        except (ValueError, TypeError):
            self.data = None

    def _value(self):
        return self.data
