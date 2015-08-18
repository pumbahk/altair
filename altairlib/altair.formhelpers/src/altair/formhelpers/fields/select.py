from wtforms import fields
from wtforms.compat import text_type
from .. import widgets as our_widgets

__all__ = [
    'AttributeStore',
    'BugFreeSelectField',
    'BugFreeSelectMultipleField',
    'LazyGroupedSelectField',
    'LazyGroupedSelectFieldBase',
    'LazyGroupedSelectMultipleField',
    'LazySelectField',
    'LazySelectFieldBase',
    'LazySelectMultipleField',
    'LazyWrapper',
    'NullStore',
    'PHPCompatibleSelectMultipleField',
    'SelectFieldDataMixin',
    'SelectMultipleFieldDataMixin',
    'WTFormsChoiceGroupsWrapper',
    'WTFormsChoicesWrapper',
    ]

class AttributeStore(object):
    def __init__(self, obj, attr_name):
        self.obj = obj
        self.attr_name = attr_name

    def has_value(self):
        return hasattr(self.obj, self.attr_name)

    def clear(self):
        try:
            delattr(self.obj, self.attr_name)
        except AttributeError:
            pass

    def get(self):
        return getattr(self.obj, self.attr_name)

    def set(self, value):
        setattr(self.obj, self.attr_name, value)

class NullStore(object):
    def __init__(self):
        self.value = None

    def has_value(self):
        return False

    def clear(self):
        return

    def get(self):
        return self.value

    def set(self, value):
        self.value = value

class LazyWrapper(object):
    def __init__(self, callable, store):
        self.callable = callable
        self.store = store

    def _get_impl(self):
        if not self.store.has_value():
            impl = self.callable()
            self.store.set(impl)
        else:
            impl = self.store.get()
        return impl

    @property
    def decoder(self):
        return self._get_impl().decoder

    @property
    def encoder(self):
        return self._get_impl().encoder

    def items(self):
        return self._get_impl().items()

    def group_iter(self):
        return self._get_impl().group_iter()

    def __len__(self):
        return len(self._get_impl())

    def __contains__(self, v):
        return v in self._get_impl()

    def __iter__(self):
        return iter(self._get_impl())

    def __getitem__(self, k):
        return self._get_impl()[k]

    def __repr__(self):
        return '<%s wrapping %r at %p>' % (self.__class__.__name__, self._get_impl(), id(self))

class WTFormsChoicesWrapper(object):
    def __init__(self, choices, coerce_getter, encoder_getter=None):
        self.choices = choices
        self.coerce_getter = coerce_getter
        self.encoder_getter = encoder_getter or (lambda: text_type)

    @property
    def encoder(self):
        return self.encoder_getter()

    @property
    def decoder(self):
        return self.coerce_getter()

    def items(self):
        coerce = self.coerce_getter()
        for encoded_value, label in self.choices:
            yield encoded_value, coerce(encoded_value), label

    def __len__(self):
        return len(self.choices)

    def __getitem__(self, v):
        encoded_v = self.encoder(v)
        for encoded_value, _ in self.choices:
            if encoded_v == encoded_value or v == encoded_value:
                return encoded_value
        raise KeyError(v)

    def __contains__(self, v):
        encoded_v = self.encoder(v)
        for encoded_value, _ in self.choices:
            if encoded_v == encoded_value or v == encoded_value:
                return True
        else:
            return False

    def __iter__(self):
        for encoded_value, label in self.choices:
            yield encoded_value

class WTFormsChoiceGroupsWrapper(object):
    def __init__(self, choice_groups, coerce_getter, encoder_getter=None):
        self.choice_groups = choice_groups
        self.coerce_getter = coerce_getter
        self.encoder_getter = encoder_getter or (lambda: text_type)

    @property
    def encoder(self):
        return self.encoder_getter()

    @property
    def decoder(self):
        return self.coerce_getter()

    def items(self):
        coerce = self.coerce_getter()
        for _, group in self.choice_groups:
            for encoded_value, label in group:
                yield encoded_value, coerce(encoded_value), label

    def group_iter(self):
        coerce = self.coerce_getter()
        def _(group):
            for encoded_value, label in group:
                yield encoded_value, coerce(encoded_value), label
        for group_name, group in self.choice_groups:
            yield group_name, _(group)

    def __len__(self):
        return sum(len(group) for _, group in self.choice_groups)

    def __contains__(self, v):
        encoded_v = self.encoder(v)
        for _, group in self.choice_groups:
            for encoded_value, _ in group:
                if encoded_v == encoded_value or v == encoded_value:
                    return True
        else:
            return False

    def __getitem__(self, v):
        encoded_v = self.encoder(v)
        for _, group in self.choice_groups:
            for encoded_value, _ in group:
                if encoded_v == encoded_value or v == encoded_value:
                    return encoded_value
        raise KeyError(v)

    def __iter__(self):
        for _, group in self.choice_groups:
            for encoded_value, label in group:
                yield encoded_value

class SelectFieldDataMixin(object):
    def process_data(self, value):
        coerce = self.coerce
        try:
            self.data = coerce(value)
        except (ValueError, TypeError):
            self.data = None

    def process_formdata(self, valuelist):
        for raw_input_filter in self.raw_input_filters:
            valuelist = raw_input_filter(valuelist)
        coerce = self.coerce
        if valuelist:
            if coerce is not None:
                try:
                    self.data = coerce(valuelist[0])
                except ValueError:
                    raise ValueError(self.gettext('Invalid Choice: could not coerce'))
            else:
                self.data = valuelist[0]

class SelectMultipleFieldDataMixin(object):
    def process_data(self, value):
        coerce = self.coerce
        try:
            self.data = [coerce(v) for v in value]
        except (ValueError, TypeError):
            self.data = None

    def process_formdata(self, valuelist):
        coerce = self.coerce
        try:
            self.data = [coerce(v) for v in valuelist]
        except ValueError:
            raise ValueError(self.gettext('Invalid Choice(s): one or more data inputs could not be coerced'))

class SelectMultipleDictFieldDataMixin(object):
    def process_data(self, value):
        coerce = self.coerce
        data = { k: False for k in self.model }
        try:
            if hasattr(value, 'items'):
                for k, v in value.items():
                    data[k] = bool(v)
            else:
                for k in value:
                    data[k] = True
        except (ValueError, TypeError) as e:
            data = None
        self.data = data

    def process_formdata(self, valuelist):
        coerce = self.coerce
        data = { k: False for k in self.model }
        try:
            for v in valuelist:
                data[coerce(v)] = True
        except (ValueError, TypeError):
            data = None
        self.data = data
        if data is None:
            raise ValueError(self.gettext('Invalid Choice(s): one or more data inputs could not be coerced'))

class LazySelectFieldBase(fields.SelectFieldBase):
    widget = our_widgets.OurSelectWidget()

    def __init__(self, label=None, validators=None, coerce=None, choices=None, model=None, cachable=None, encoder=None, **kwargs):
        _form = kwargs.get('_form')
        hide_on_new = kwargs.pop('hide_on_new', False)
        raw_input_filters = kwargs.pop('raw_input_filters', [])
        if callable(label):
            label = label()
        super(LazySelectFieldBase, self).__init__(label, validators, **kwargs)
        self._form = _form
        self.hide_on_new = hide_on_new
        self.raw_input_filters = raw_input_filters
        for base in self.__class__.__bases__[1:]:
            if hasattr(base, '__mixin_init__'):
                base.__mixin_init__(self, label, validators, coerce, choices, model, cachable, **kwargs)
        if choices is not None:
            if callable(choices):
                self._model = LazyWrapper(
                    lambda: WTFormsChoicesWrapper(choices(self), lambda: self._coerce or text_type, lambda: self._encoder or text_type),
                    AttributeStore(self, '_choices_cache') if cachable is None or cachable else NullStore())
            else:
                if cachable is not None:
                    raise TypeError('cachable is specified but choices will not be initialized lazily')
                self._model = WTFormsChoicesWrapper(choices, lambda: self._coerce or text_type, lambda: self._encoder or text_type)

        elif model is not None:
            if callable(model):
                self._model = LazyWrapper(
                    lambda: model(self),
                    AttributeStore(self, '_choices_cache') if cachable is None or cachable else NullStore())
            else:
                if cachable is not None:
                    raise TypeError('cachable is specified but choices will not be initialized lazily')
                self._model = model
        else:
            self._model = None

        self._coerce = coerce
        self._encoder = encoder

    def _get_coerce(self):
        if self._coerce is not None:
            return self._coerce
        else:
            if self._model is not None:
                decoder = getattr(self._model, 'decoder', None)
                if decoder:
                    return decoder
                else:
                    raise TypeError('no decoder is provided for %r' % self._model)
            return None

    def _set_coerce(self, value):
        self._coerce = value

    coerce = property(_get_coerce, _set_coerce)

    def _get_choices(self):
        if self._model is not None:
            return [(encoded_value, label) for encoded_value, model_value, label in self._model.items()]
        else:
            return []

    def _set_choices(self, value):
        self._model = WTFormsChoicesWrapper(value, lambda: self._coerce or text_type, lambda: self._encoder or text_type)

    choices = property(_get_choices, _set_choices)

    @property
    def model(self):
        return self._model

    def iter_choices(self):
        if self._model is not None:
            for encoded_value, model_value, label in self._model.items():
                yield (encoded_value, label, model_value == self.data)

    def pre_validate(self, form):
        if self.model and self.data not in self.model:
            raise ValueError(self.gettext('Not a valid choice'))

    def _value(self):
        return self.model[self.data]

class LazySelectField(SelectFieldDataMixin, LazySelectFieldBase):
    pass

class LazySelectMultipleField(SelectMultipleFieldDataMixin, LazySelectFieldBase):
    widget = our_widgets.OurSelectWidget(multiple=True)

    def iter_choices(self):
        for encoded_value, model_value, label in self.model.items():
            yield (encoded_value, label, self.data is not None and \
                                         model_value in self.data)

    def pre_validate(self, form):
        if self.data:
            for d in self.data:
                if d not in self.model:
                    raise ValueError(self.gettext("'%(value)s' is not a valid choice for this field" % dict(value=d)))

class LazySelectMultipleDictField(SelectMultipleDictFieldDataMixin, LazySelectFieldBase):
    widget = our_widgets.OurSelectWidget(multiple=True)

    def iter_choices(self):
        for encoded_value, model_value, label in self.model.items():
            yield (encoded_value, label, self.data is not None and \
                                         self.data[model_value])

    def pre_validate(self, form):
        if self.data:
            for d in self.data:
                if d not in self.model:
                    raise ValueError(self.gettext("'%(value)s' is not a valid choice for this field" % dict(value=d)))


class LazyGroupedSelectFieldBase(fields.SelectFieldBase):
    def __init__(self, label=None, validators=None, coerce=None, choices=None, model=None, cachable=None, encoder=None, **kwargs):
        _form = kwargs.get('_form')
        hide_on_new = kwargs.pop('hide_on_new', False)
        raw_input_filters = kwargs.pop('raw_input_filters', [])
        if callable(label):
            label = label()
        super(LazyGroupedSelectFieldBase, self).__init__(label, validators, **kwargs)
        self._form = _form
        self.hide_on_new = hide_on_new
        self.raw_input_filters = raw_input_filters
        for base in self.__class__.__bases__[1:]:
            if hasattr(base, '__mixin_init__'):
                base.__mixin_init__(self, label, validators, coerce, choices, model, cachable, **kwargs)
        if choices is not None:
            if callable(choices):
                self._model = LazyWrapper(
                    lambda: WTFormsChoiceGroupsWrapper(choices(self), lambda: self._coerce or text_type, lambda: self._encoder or text_type),
                    AttributeStore(self, '_choices_cache') if cachable is None or cachable else NullStore())
            else:
                if cachable is not None:
                    raise TypeError('cachable is specified but choices will not be initialized lazily')
                self._model = WTFormsChoiceGroupsWrapper(choices, lambda: self._coerce or text_type, lambda: self._encoder or text_type)

        elif model is not None:
            if callable(model):
                self._model = LazyWrapper(
                    lambda: model(self),
                    AttributeStore(self, '_choices_cache') if cachable is None or cachable else NullStore())
            else:
                if cachable is not None:
                    raise TypeError('cachable is specified but choices will not be initialized lazily')
                self._model = model
        else:
            raise TypeError('either choices or model must be a non-None value')

        self._coerce = coerce
        self._encoder = encoder

    def _get_coerce(self):
        if self._coerce is not None:
            return self._coerce
        else:
            decoder = getattr(self.model, 'decoder', None)
            if decoder:
                return decoder
            else:
                raise TypeError('no decoder is provided for %r' % self.model)

    def _set_coerce(self, value):
        self._coerce = value

    coerce = property(_get_coerce, _set_coerce)

    def _get_choices(self):
        return [(encoded_value, label) for encoded_value, model_value, label in self._choices]

    def _set_choices(self, value):
        self._model = WTFormsChoiceGroupsWrapper(value, lambda: self._coerce or text_type, lambda: self._encoder or text_type)

    choices = property(_get_choices, _set_choices)

    @property
    def model(self):
        return self._model

    def iter_choice_groups(self):
        def _(choice_iter):
            for encoded_value, model_value, label in choice_iter:
                yield (encoded_value, label, model_value == self.data)

        for group_name, choice_iter in self.model.group_iter():
            yield group_name, _(choice_iter)

class LazyGroupedSelectField(SelectFieldDataMixin, LazyGroupedSelectFieldBase):
    widget = our_widgets.GroupedSelect()

    def pre_validate(self, form):
        if self.data not in self.model:
            raise ValueError(self.gettext('Not a valid choice'))

class LazyGroupedSelectMultipleField(SelectMultipleFieldDataMixin, LazyGroupedSelectFieldBase):
    widget = our_widgets.GroupedSelect(multiple=True)

    def iter_choice_groups(self):
        def _(choice_iter):
            for encoded_value, model_value, label in choice_iter:
                yield (encoded_value, label, self.data is not None and \
                                             model_value in self.data)

        for group_name, choice_iter in self.model.group_iter():
            yield group_name, _(choice_iter)

    def pre_validate(self, form):
        if self.data:
            for d in self.data:
                if d not in self.model:
                    raise ValueError(self.gettext("'%(value)s' is not a valid choice for this field" % dict(value=d)))


BugFreeSelectField = LazySelectField
BugFreeSelectMultipleField = LazySelectMultipleField

class PHPCompatibleSelectMultipleField(LazySelectMultipleField):
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
