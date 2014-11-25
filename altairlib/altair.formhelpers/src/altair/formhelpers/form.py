from wtforms import form, fields
from wtforms.ext.csrf import SecureForm
from wtforms.ext.csrf.session import SessionSecureForm
from wtforms.fields.core import UnboundField
from wtforms.compat import iteritems
from .fields.liaison import Liaison

__all__ = [
    'OurForm',
    'OurSecureForm',
    'OurDynamicForm',
    ]

class OurForm(form.Form):
    def __init__(self, *args, **kwargs):
        self.new_form = kwargs.pop('new_form', False)
        self._name_builder = kwargs.pop('name_builder', None)
        self._liaisons = fields and [name for name, unbound_field in self._unbound_fields if unbound_field.field_class == Liaison]
        super(OurForm, self).__init__(*args, **kwargs)

    def __setitem__(self, overridden, name, value):
        self._field[name] = value.bind(form=self, name=name, prefix=self._prefix, name_builder=self._name_builder)

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

class OurDynamicForm(OurForm):
    def __init__(self, formdata=None, obj=None, prefix='', *args, **kwargs):
        dynamic_fields = kwargs.pop('_fields', [])
        self._translations = kwargs.pop('_translations', None)
        self._initializing = dynamic_fields
        super(OurDynamicForm, self).__init__(formdata, obj, prefix, *args, **kwargs)
        self._initializing = False
        super(OurDynamicForm, self).process(formdata, obj, **kwargs)

    def _get_translations(self):
        if callable(self._translations):
            return self._translations()
        else:
            return self._translations

    def process(self, formdata=None, obj=None, **kwargs):
        if self._initializing:
            translations = self._get_translations()
            unbound_fields = list(self._unbound_fields)
            for name, unbound_field in self._initializing:
                field = unbound_field.bind(form=self, name=name, prefix=self._prefix, translations=translations, name_builder=self._name_builder)
                self._fields[name] = field
                unbound_fields.append((name, unbound_field))
            self._unbound_fields = unbound_fields
        else:
            return super(OurDynamicForm, self).process(formdata=formdata, obj=obj, **kwargs)

    def validate(self, extra={}):
        return super(form.Form, self).validate(extra)

class OurSecureForm(OurForm, SecureForm):
    def __init__(self, formdata=None, obj=None, prefix='', csrf_context=None, **kwargs):
        super(OurSecureForm, self).__init__(formdata, obj, prefix, csrf_context=csrf_context, **kwargs)

class OurSessionSecureForm(OurSecureForm, SessionSecureForm):
    pass
