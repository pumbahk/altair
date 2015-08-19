import json
import re
import itertools
from collections import OrderedDict
from wtforms import fields
from wtforms.fields.core import _unset_value
from wtforms.compat import iteritems
from wtforms.widgets import html_params, HTMLString
from ..widgets import OurInput, OurTextInput, OurPasswordInput, OurTextArea, OurCheckboxInput, OurRadioInput, OurFileInput, OurListWidget, OurTableWidget
from ..widgets.select import SelectRendrant
from zope.deprecation import deprecation
from .select import (
    LazySelectField,
    LazySelectMultipleField,
    LazySelectMultipleDictField,
    LazyGroupedSelectField,
    LazyGroupedSelectMultipleField,
    PHPCompatibleSelectMultipleField,
    )
from ..utils.mixin import (
    override,
    make_class_factory,
    )

__all__ = [
    'RendererMixin',
    'OurFieldMixin',
    'OurField',
    'OurLabel',
    'OurHiddenField',
    'OurRadioField',
    'OurTextField',
    'OurTextAreaField',
    'OurSelectField',
    'OurSelectMultipleField',
    'OurSelectMultipleDictField',
    'OurPHPCompatibleSelectMultipleField',
    'OurGroupedSelectField',
    'OurGroupedSelectMultipleField',
    'OurDecimalField',
    'OurIntegerField',
    'OurFloatField',
    'OurBooleanField',
    'OurDecimalField',
    'NullableTextField',
    'NullableIntegerField',
    'SimpleElementNameHandler',
    'OurFormField',
    'JSONField',
    'DelimitedTextsField',
    'OurGenericFieldList',
    'OurPHPCompatibleFieldList',
    ]

field_class_factory = make_class_factory(type)

class RendererMixin(object):
    def __mixin_init_pre__(self, **kwargs):
        self.widget_stack = []
        return kwargs

    def _push_widget(self, widget):
        self.widget_stack.append(self.widget)
        self.widget = widget

    def _pop_widget(self):
        self.widget = self.widget_stack.pop()

    def _render(self, *args, **kwargs):
        __callee = kwargs.pop('__callee')
        widget_override = kwargs.pop('_widget', None)
        if widget_override is not None:
            self._push_widget(widget_override)
        try:
            return __callee(self, *args, **kwargs)
        finally:
            if widget_override is not None:
                self._pop_widget()


class OurFieldMixin(object):
    def __mixin_init_pre__(self, **kwargs):
        _form = kwargs.get('_form', None)
        hide_on_new = kwargs.pop('hide_on_new', False)
        help = kwargs.pop('help', None)
        name_builder = kwargs.pop('name_builder', None)
        if name_builder is None and _form is not None:
            name_builder = getattr(_form, '_name_builder', None)
        if name_builder is not None:
            kwargs.pop('prefix', None)
        raw_input_filters = kwargs.pop('raw_input_filters', [])
        if 'label' in kwargs:
            label = kwargs['label']
            if callable(label):
                label = label()
                kwargs['label'] = label

        self._form = _form
        self._name_builder = name_builder
        self.hide_on_new = hide_on_new
        self._validation_stopped = False

        self.raw_input_filters = raw_input_filters
        description = kwargs.pop('description', u'')
        if callable(description):
            description = description(self)
        self._description = description
        kwargs['description'] = description
        note = kwargs.pop('note', u'')
        if callable(note):
            note = note(self)
        self._note = note
        self.help = help
        return kwargs

    @property
    @deprecation.deprecate(u"use field._form")
    def form(self):
        return self._form

    def __mixin_init_post__(self, **kwargs):
        self.label = OurLabel(self.label.field_id, self.label.text)
        self.reset_name_builder()

    def reset_name_builder(self):
        if self._name_builder is not None:
            self.name = self._name_builder(self.short_name)

    @property
    def name_builder(self):
        return self._name_builder

    @name_builder.setter
    def name_builder(self, value):
        self._name_builder = value
        self.reset_name_builder()

    @override
    def process_formdata(self, overridden, valuelist):
        for raw_input_filter in self.raw_input_filters:
            valuelist = raw_input_filter(valuelist)
        return overridden(self, valuelist)

    @override
    def __call__(self, overridden, *args, **kwargs):
        if hasattr(self, '_render'):
            return self._render(__callee=overridden, *args, **kwargs)
        else:
            return overridden(self, *args, **kwargs)

    @override
    def post_validate(self, overridden, form, validation_stopped):
        self._validation_stopped = validation_stopped
        overridden(self, form, validation_stopped)

class Singleton(object):
    def __init__(self, key, value):
        self.key = [key]
        self.value = [value]

    def getlist(self, k):
        if self.key[0] != k:
            return []
        else:
            return self.value

    def __getitem__(self, k):
        if self.key[0] != k:
            raise KeyError(k)
        return self.value[0]

    def __len__(self):
        return 1

    def __iter__(self):
        return iter(self.key)


class OurLabel(fields.Label):
    def __call__(self, text=None, field_id=None, **kwargs):
        kwargs['for'] = self.field_id if field_id is None else field_id
        attributes = html_params(**kwargs)
        return HTMLString('<label %s>%s</label>' % (attributes, text or self.text))


class OurField(fields.Field, RendererMixin, OurFieldMixin):
    __metaclass__ = field_class_factory

class OurHiddenField(fields.HiddenField, RendererMixin, OurFieldMixin):
    __metaclass__ = field_class_factory

class OurRadioField(fields.RadioField, RendererMixin, OurFieldMixin):
    __metaclass__ = field_class_factory
    widget = OurListWidget(prefix_label=False)

class OurTextField(fields.TextField, RendererMixin, OurFieldMixin):
    __metaclass__ = field_class_factory
    widget = OurTextInput()

class OurTextAreaField(fields.TextAreaField, RendererMixin, OurFieldMixin):
    __metaclass__ = field_class_factory
    widget = OurTextArea()

class OurSelectField(LazySelectField, RendererMixin, OurFieldMixin):
    __metaclass__ = field_class_factory

class OurSelectMultipleField(LazySelectMultipleField, RendererMixin, OurFieldMixin):
    __metaclass__ = field_class_factory

class OurSelectMultipleDictField(LazySelectMultipleDictField, RendererMixin, OurFieldMixin):
    __metaclass__ = field_class_factory

class OurPHPCompatibleSelectMultipleField(PHPCompatibleSelectMultipleField, RendererMixin, OurFieldMixin):
    __metaclass__ = field_class_factory

class OurGroupedSelectField(LazyGroupedSelectField, RendererMixin, OurFieldMixin):
    __metaclass__ = field_class_factory

class OurGroupedSelectMultipleField(LazyGroupedSelectMultipleField, RendererMixin, OurFieldMixin):
    __metaclass__ = field_class_factory

class OurDecimalField(fields.DecimalField, RendererMixin, OurFieldMixin):
    __metaclass__ = field_class_factory
    widget = OurTextInput()

    def build_js_coercer(self):
        return u'''function (d) { return parseFloat(d.replace(/^\\s+|\\s+$/, '')); }'''

class OurIntegerField(fields.IntegerField, RendererMixin, OurFieldMixin):
    __metaclass__ = field_class_factory
    widget = OurTextInput()

    def build_js_coercer(self):
        return u'''function (d) { return parseInt(d.replace(/^\\s+|\\s+$/, '')); }'''
 
class OurFloatField(fields.FloatField, RendererMixin, OurFieldMixin):
    __metaclass__ = field_class_factory
    widget = OurTextInput()

    def build_js_coercer(self):
        return u'''function (d) { return parseFloat(d.replace(/^\\s+|\\s+$/, '')); }'''

class OurBooleanField(fields.BooleanField, RendererMixin, OurFieldMixin):
    __metaclass__ = field_class_factory
    widget = OurCheckboxInput()

    def process_formdata(self, valuelist):
        def b(v):
            if isinstance(v, bool):
                return v
            else:
                try:
                    return len(v) > 0
                except TypeError as e:
                    return False
        self.data = any(b(v) for v in valuelist)

    def build_js_coercer(self):
        return u'''function (d) { return parseInt(d.replace(/^\\s+|\\s+$/, '')) != 0; }'''

class NullableTextField(OurTextField):
    def process_formdata(self, valuelist):
        if not valuelist or valuelist[0] == '':
            self.data = None
        else:
            super(NullableTextField, self).process_formdata(valuelist)

class NullableIntegerField(OurIntegerField):
    def process_formdata(self, valuelist):
        if not valuelist or valuelist[0] == '':
            self.data = None
        else:
            super(NullableIntegerField, self).process_formdata(valuelist)


class SimpleElementNameHandler(object):
    def __init__(self, separator):
        self.separator = separator

    def build(self, field_name, subfield_name):
        return u'%s%s%s' % (field_name, self.separator, subfield_name)

    def resolve(self, combined_name):
        field_name, s, subfield_name = combined_name.partition(self.separator)
        if subfield_name is None:
            return None, None
        return field_name, subfield_name

    def display_name(self, field, subfield):
        return u'%s - %s' % (field.label, subfield.label)


class OurFormField(OurField):
    widget = OurTableWidget()
 
    def __init__(self, form_factory, label=None, validators=None, name_handler='-', field_error_formatter='%(name)s: %(message)s', **kwargs):
        super(OurFormField, self).__init__(label, validators, **kwargs)
        self.form_factory = form_factory
        if isinstance(name_handler, basestring):
            name_handler = SimpleElementNameHandler(name_handler)

        self._name_handler = name_handler
        self._obj = None
        self._contained_form = None
        if isinstance(field_error_formatter, basestring):
            field_error_formatter = (
                lambda field_error_format: \
                    lambda self, name, message: \
                        field_error_format % dict(name=name, message=message)
                )(field_error_formatter)
        self._field_error_formatter = field_error_formatter

    def _build_subfield_name(self, subfield_name):
        return self._name_handler.build(self.name, subfield_name)

    def process(self, formdata, data=_unset_value):
        if data is _unset_value:
            try:
                data = self.default()
            except TypeError:
                data = self.default
            self._obj = data

        self.object_data = data

        if isinstance(data, dict):
            form = self.form_factory(formdata=formdata, name_builder=self._build_subfield_name, _containing_field=self, **data)
        else:
            form = self.form_factory(formdata=formdata, name_builder=self._build_subfield_name, obj=data, _containing_field=self)
        self._contained_form = form

    def post_validate(self, form, validation_stopped):
        super(OurFormField, self).post_validate(form, validation_stopped)
        if not validation_stopped:
            if not self._contained_form.validate():
                if self._field_error_formatter is not None:
                    for k, v in iteritems(self._contained_form.errors):
                        display_name = self._name_handler.display_name(self, getattr(self._contained_form, k))
                        if display_name is not None and self._field_error_formatter:
                            self.errors.append(self._field_error_formatter(self, display_name, v))
                else:
                    self.errors = self._contained_form.errors

    def populate_obj(self, obj, name):
        candidate = getattr(obj, name, None)
        if candidate is None:
            if self._obj is None:
                raise TypeError('populate_obj: cannot find a value to populate fom the provided obj or input data/defaults')
            candidate = self._obj
            setattr(obj, name, candidate)

        self.form.populate_obj(candidate)

    @property
    def data(self):
        return self._contained_form.data

    def __len__(self):
        return len(self._contained_form._fields)

    def __iter__(self):
        return iter(self._contained_form)

    def __contains__(self, k):
        return k in self._contained_form

    def __getitem__(self, k):
        return self._contained_form[k]

    def __getattr__(self, k):
        return getattr(self._contained_form, k)

class JSONField(fields.Field, RendererMixin, OurFieldMixin):
    def _value(self):
        if self.raw_data:
            return self.raw_data[0]
        elif self.data is not None:
            return json.dumps(self.data)
        else:
            return u''

    def process_formdata(self, valuelist):
        self.data = None
        if valuelist:
            try:
                self.data = json.loads(valuelist[0])
            except (TypeError, ValueError):
                raise ValueError(self.gettext('Invalid JSON value'))


class DelimitedTextsField(fields.Field, RendererMixin, OurFieldMixin):
    def _value(self):
        if self.raw_data:
            return self.raw_data[0]
        elif self.data is not None:
            return self.canonical_delimiter.join(self.data)
        else:
            return u''

    def strip(self, value):
        return re.sub(
            self.delimiter_pattern + ur'$', u'',
            re.sub(ur'^' + self.delimiter_pattern, u'', value)
            )

    def process_formdata(self, valuelist):
        self.data = None
        if valuelist:
            try:
                self.data = re.split(self.delimiter_pattern, self.strip(valuelist[0]))
            except:
                raise ValueError(self.gettext('Invalid string'))

    def __init__(self, *args, **kwargs):
        delimiter_pattern = kwargs.pop('delimiter_pattern')
        canonical_delimiter = kwargs.pop('canonical_delimiter')
        super(DelimitedTextsField, self).__init__(*args, **kwargs)
        self.delimiter_pattern = delimiter_pattern
        self.canonical_delimiter = canonical_delimiter


class OurGenericFieldList(fields.Field, RendererMixin, OurFieldMixin):
    class _fake(object):
        __slot__ = ['data']

    widget = OurListWidget()

    def __init__(self, unbound_field, label=None, validators=None, default={}, **kwargs):
        _prefix = kwargs.pop('_prefix', None)
        name_handler = kwargs.pop('name_handler', None)
        super(OurFieldList, self).__init__(
            label=label,
            validators=validators,
            default=default,
            **kwargs
            )
        if name_handler is None and _prefix is not None:
            name_handler = _prefix
        if isinstance(name_handler, basestring):
            name_handler = SimpleElementNameHandler(name_handler)
        self._name_handler = name_handler


    def _build_subfield_name(self, subfield_name):
        return self._name_handler.build(self.name, subfield_name)

    def process(self, formdata, data=_unset_value):
        if data is _unset_value or not data:
            try:
                data = self.default()
            except TypeError:
                data = self.default

        self.object_data = data

        entries = OrderedDict()
        if formdata:
            indices = [
                (subfield_name, k)
                for field_name, subfield_name in (
                    self._name_handler.resolve(k)
                    for k in formdata
                    )
                if field_name is not None and field_name == self.name
                ]
            for subfield_name, k in indices:
                subfield_raw_values = formdata.getlist(k)
                obj_data = data.get(subfield_name, [])
                for subfield_raw_value, subfield_data in itertools.izip_longest(subfield_raw_values, obj_data, fillvalue=_unset_value):
                    field = self.unbound_field.bind(form=None, name=subfield_name, translations=self._translations, name_builder=self._build_subfield_name)
                    field.process(
                        Singleton(k, subfield_raw_value) if subfield_raw_value is not _unset_value else None,
                        subfield_data
                        )
                    entries.setdefault(subfield_name, []).append(field)
        else:
            for subfield_name, obj_data in data.items():
                for subfield_data in obj_data:
                    field = self.unbound_field.bind(form=None, name=subfield_name, translations=self._translations, name_builder=self._build_subfield_name)
                    field.process(None, subfield_data)
                    entries.setdefault(subfield_name, []).append(field)
        self.entries = entries

    def validate(self, form, extra_validators=tuple()):
        self.errors = []
        success = True
        for _, subfields in self.entries.items():
            for subfield in subfields:
                if not subfield.validate(form):
                    success = False
                    self.errors.append(subfield.errors)
        return success

    def populate_obj(self, obj, name):
        data = getattr(obj, name, None)
        output = OrderedDict()
        for subfield_name, obj_data in data.items():
            obj_data = []
            subfields = self.entries[subfield_name]
            for subfield, subfield_data in itertools.izip(obj_data, itertools.chain(subfields, itertools.repeat(None))):
                if subfield is not None:
                    fake_obj = self._fake(data)
                    subfield.populate_obj(fake_obj, 'data')
                obj_data.append(fake_obj.data)
            output[subfield_name] = obj_data
        setattr(obj, name, output)

    def __iter__(self):
        return iter(self.entries)

    def __len__(self):
        return len(self.entries)

    @property
    def data(self):
        return OrderedDict(
            (subfield_name, 
                [
                    subfield.data
                    for subfield in subfields
                    ]
                )
            for subfield_name, subfields in self.entries.items()
            )


class OurPHPCompatibleFieldList(fields.Field, RendererMixin, OurFieldMixin):
    class _fake(object):
        __slot__ = ['data']

    widget = OurListWidget()

    def __init__(self, unbound_field, label=None, validators=None, default=(), min_entries=0, max_entries=None, **kwargs):
        self.min_entries = min_entries
        self.max_entries = max_entries
        self._subfield_name = None
        self.unbound_field = unbound_field
        super(OurPHPCompatibleFieldList, self).__init__(
            label=label,
            validators=validators,
            default=default,
            **kwargs
            )

    def _build_subfield_name(self):
        if self._subfield_name is None:
            self._subfield_name = u'%s[]' % self.name
        return self._subfield_name

    def process(self, formdata, data=_unset_value):
        if data is _unset_value or not data:
            try:
                data = self.default()
            except TypeError:
                data = self.default

        data = list(data)
        subfield_name = self._build_subfield_name()

        entries = []
        if formdata:
            subfield_raw_values = []
            for k in formdata:
                if k.startswith(self.name) and k[len(self.name):] == u'[]':
                    subfield_raw_values = formdata.getlist(k)
            if self.max_entries:
                subfield_raw_values = subfield_raw_values[:self.max_entries]
                data = data[:self.max_entries]

            if len(subfield_raw_values) < self.min_entries:
                for i in range(0, self.min_entries - len(values)):
                    subfield_raw_values.append(_unset_value)
            if len(data) < self.min_entries:
                for i in range(0, self.min_entries - len(data)):
                    data.append(_unset_value)

            for subfield_raw_value, subfield_data in itertools.izip_longest(subfield_raw_values, data, fillvalue=_unset_value):
                field = self.unbound_field.bind(form=None, name=subfield_name, translations=self._translations)
                field.process(
                    Singleton(
                        subfield_name,
                        subfield_raw_value
                        ) \
                        if subfield_raw_value is not _unset_value \
                        else None,
                    subfield_data
                    )
                entries.append(field)
        else:
            if self.max_entries:
                data = data[:self.max_entries]
            if len(data) < self.min_entries:
                for i in range(0, self.min_entries - len(data)):
                    data.append(_unset_value)
            for subfield_data in data:
                field = self.unbound_field.bind(form=None, name=subfield_name, translations=self._translations)
                field.process(
                    None,
                    subfield_data
                    )
                entries.append(field)
        self.object_data = data
        self.entries = entries

    def validate(self, form, extra_validators=tuple()):
        self.errors = []
        success = True
        for subfield in self.entries:
            if not subfield.validate(form):
                success = False
                self.errors.append(subfield.errors)
        return success

    def populate_obj(self, obj, name):
        output = []
        for subfield in self.entries:
            if subfield is not None:
                fake_obj = self._fake(data)
                subfield.populate_obj(fake_obj, 'data')
                data = fake_obj.data
            else:
                data = _unset_value
            output.append(fake_obj.data)
        setattr(obj, name, output)

    def __iter__(self):
        return iter(self.entries)

    def __len__(self):
        return len(self.entries)

    @property
    def data(self):
        return [
            subfield.data
            for subfield in self.entries
            ]

