from wtforms.fields import StringField
from altair.formhelpers.fields import OurSelectField
from wtforms.widgets import TextInput

__all__ = (
  'StringFieldWithChoice',
  )

class StringFieldWithChoice(StringField, OurSelectField):
    widget = TextInput()

    def __coerce(self, value):
        return self.coerce(value) if value is not None else ''

    def process_data(self, value):
        try:
            self.data = self.__coerce(value)
        except (ValueError, TypeError):
            self.data = None

    def _value(self):
        return self.data if self.data is not None else ''
