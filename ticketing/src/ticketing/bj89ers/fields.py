from wtforms.fields import StringField, SelectField
from wtforms.widgets import TextInput

__all__ = (
  'TextFieldWithChoice',
  )

class StringFieldWithChoice(StringField, SelectField):
    widget = TextInput()

    def _value(self):
        return self.coerce(self.data) if self.data is not None else ''
