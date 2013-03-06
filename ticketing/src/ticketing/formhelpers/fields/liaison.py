from wtforms import fields

class Liaison(fields.Field):
    @property
    def errors(self):
        return self._wrapped.errors

    @property
    def process_errors(self):
        return self._wrapped.process_errors

    @property
    def raw_data(self):
        return self._wrapped.raw_data

    @property
    def validators(self):
        return self._wrapped.validators

    @property
    def widget(self):
        return self._wrapped.widget

    @property
    def _translations(self):
        return self._wrapped._translations

    @property
    def do_not_call_in_templates(self):
        return self._wrapped.do_not_call_in_templates

    @property
    def data(self):
        return self._wrapped.data

    @property
    def form(self):
        return self._form

    @property
    def data(self):
        return self._data

    def gettext(self, string):
        return self._wrapped.gettext(string)

    def ngettext(self, singular, plural, n):
        return self._wrapped.ngettext(singular, plural, n)

    def validate(self, *args, **kwargs):
        return self._wrapped.validate(*args, **kwargs)

    def pre_validate(self, form):
        return self._wrapped.pre_validate(self, form)

    def post_validate(self, form, validation_stopped):
        return self._wrapped.post_validate(form, validation_stopped)

    def process(self, formdata=None, data=fields._unset_value):
        return self._wrapped.process(formdata, data)

    def validate(self, form, extra_validators=()):
        return self._wrapped.validate(form, extra_validators)

    def populate_obj(self, obj, name):
        return self._wrapped.populate_obj(obj, name)

    def append_entry(self, data=fields._unset_value):
        return self._wrapped.append_entry(data)

    def pop_entry(self):
        return self._wrapped.pop_entry()

    def __iter__(self):
        return self._wrapped.__iter__()

    def __len__(self):
        return self._wrapped.__len__()

    def __unicode__(self):
        return self._wrapped.__unicode__()

    def __str__(self):
        return self._wrapped.__str__()

    def __html__(self):
        return self._wrapped.__html__()

    def __call__(self, **kwargs):
        return self._wrapped(**kwargs)

    def __getitem__(self, index):
        return self._wrapped.__getitem__(index)

    def __getattr__(self, key):
        return getattr(self._wrapped, key)

    def __setattr__(self, key, value):
        if not key.startswith('_'):
            setattr(self._wrapped, key, value)
        else:
            object.__setattr__(self, key, value)

    def __init__(self, counterpart, wrapped, _form=None, _name=None, _prefix=None, _translations=None, **kwargs):
        if counterpart.__class__ == fields.core.UnboundField:
            # resolve the field name from the unbound field object.
            for name, unbound_field in _form._unbound_fields:
                if unbound_field == counterpart:
                    counterpart = name
        self._counterpart = counterpart
        self._form = _form
        self._name = _name
        self._wrapped = wrapped.bind(_form, _name, _prefix, _translations, **kwargs)
