from wtforms import fields

class BugFreeSelectField(fields.SelectField):
    def pre_validate(self, form):
        for v, _ in self.choices:
            if self.data == self.coerce(v):
                break
        else:
            raise ValueError(self.gettext('Not a valid choice'))

class BugFreeSelectMultipleField(fields.SelectMultipleField):
    def pre_validate(self, form):
        if self.data is not None:
            for d in self.data:
                for v, _ in self.choices:
                    if d == self.coerce(v):
                        break
                else:
                    raise ValueError(self.gettext('Not a valid choice'))

class PHPCompatibleSelectMultipleField(BugFreeSelectMultipleField):
    def process(self, formdata, data=fields._unset_value):
        self.process_errors = []
        if data is fields._unset_value:
            try:
                data = self.default()
            except TypeError:
                data = self.default

        self.object_data = data

        try:
            self.process_data(data)
        except ValueError as e:
            self.process_errors.append(e.args[0])

        if formdata:
            php_styled_collection_key = self.name + '[]'
            try:
                if self.name in formdata:
                    self.raw_data = formdata.getlist(self.name)
                elif php_styled_collection_key in formdata:
                    self.raw_data = formdata.getlist(php_styled_collection_key)
                else:
                    self.raw_data = []
                self.process_formdata(self.raw_data)
            except ValueError as e:
                self.process_errors.append(e.args[0])

        for filter in self.filters:
            try:
                self.data = filter(self.data)
            except ValueError as e:
                self.process_errors.append(e.args[0])

def _gen_field_init(klass):
    def __init__(self, _form=None, hide_on_new=False, *args, **kwargs):
        super(klass, self).__init__(*args, **kwargs)
        self.form = _form
        self.hide_on_new=hide_on_new
    klass.__init__ = __init__

class OurTextField(fields.TextField):
    pass

_gen_field_init(OurTextField)

class OurSelectField(BugFreeSelectField):
    pass

_gen_field_init(OurSelectField)

class OurDecimalField(fields.DecimalField):
    pass

_gen_field_init(OurDecimalField)

class OurIntegerField(fields.IntegerField):
    pass

_gen_field_init(OurIntegerField)

class OurBooleanField(fields.BooleanField):
    pass
_gen_field_init(OurBooleanField)

class NullableTextField(OurTextField):
    def process_formdata(self, valuelist):
        super(NullableTextField, self).process_formdata(valuelist)
        if self.data == '':
            self.data = None
