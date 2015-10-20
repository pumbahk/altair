# encoding: utf-8

import re
from wtforms import validators

class Required(validators.DataRequired):
    def __call__(self, form, field):
        # allow Zero input
        if field.data != 0:
            super(Required, self).__call__(form, field)

class RequiredOnUpdate(validators.Required):
    def __init__(self):
        self.delegated = Required()

    def __call__(self, form, field):
        if not getattr(form, 'new_form', False):
            self.delegated(form, field)

class RequiredOnNew(validators.Required):
    def __init__(self):
        self.delegated = Required()

    def __call__(self, form, field):
        if getattr(form, 'new_form', False):
            self.delegated(form, field)



