from wtforms import form, fields
from wtforms.compat import iteritems
from .fields.liaison import Liaison

class OurForm(form.Form):
    def __init__(self, *args, **kwargs):
        self.new_form = kwargs.pop('new_form', False)
        self._liaisons = fields and [name for name, unbound_field in self._unbound_fields if unbound_field.field_class == Liaison]
        super(OurForm, self).__init__(*args, **kwargs)

    def process(self, formdata=None, obj=None, **kwargs):
        if not self._liaisons:
            return super(OurForm, self).process(formdata, obj, **kwargs)

        if formdata is not None and not hasattr(formdata, 'getlist'):
            if hasattr(formdata, 'getall'): 
                formdata = form.WebobInputWrapper(formdata)
            else:
                raise TypeError("formdata should be a multidict-type wrapper that supports the 'getlist' method: ")

        for name, field in iteritems(self._fields):
            if obj is not None and hasattr(obj, name):
                field.process(formdata, getattr(obj, name))
            elif name in kwargs:
                field.process(formdata, kwargs[name])
            else:
                field.process(formdata)

        for name in self._liaisons:
            liaison = self._fields[name]
            counterpart = self._fields[liaison._counterpart]
            if not counterpart.data:
                counterpart.data = liaison.data
                liaison.data = None

