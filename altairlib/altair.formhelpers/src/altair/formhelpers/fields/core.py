import json
from wtforms import fields
from wtforms.fields.core import _unset_value
from wtforms.compat import iteritems
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

class OurField(fields.Field, RendererMixin, OurFieldMixin):
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
