import re
from wtforms import validators as _v

class Email(_v.Regexp):
    def __init__(self, message=None):
        super(Email, self).__init__(r'^[a-zA-Z_+\-*/=]+@[^.][a-zA-Z_\-.]*\.[a-z]{2,10}$', re.IGNORECASE, message)

    def __call__(self, form, field):
        if self.message is None:
            self.message = field.gettext(u'Invalid email address.')

        super(Email, self).__call__(form, field)
