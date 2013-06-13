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

class RendererMixin(object):
    def __mixin_init__(self, *args, **kwargs):
        self.widget_stack = []

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


def _gen_field_init(klass):
    prev_call = klass.__call__

    def __init__(self, *args, **kwargs):
        _form  = kwargs.pop('_form', None)
        hide_on_new = kwargs.pop('hide_on_new', False)
        super(klass, self).__init__(*args, **kwargs)
        self.form = _form
        self.hide_on_new = hide_on_new
        for base in self.__class__.__bases__[1:]:
            if hasattr(base, '__mixin_init__'):
                base.__mixin_init__(self, *args, **kwargs)

    def __call__(self, *args, **kwargs):
        if hasattr(self, '_render'):
            return self._render(__callee=prev_call, *args, **kwargs)
        else:
            return prev_call(self, *args, **kwargs)
    klass.__init__ = __init__
    klass.__call__ = __call__
    return klass

@_gen_field_init
class OurRadioField(fields.RadioField, RendererMixin):
    pass

@_gen_field_init
class OurTextField(fields.TextField, RendererMixin):
    pass

@_gen_field_init
class OurSelectField(BugFreeSelectField, RendererMixin):
    pass

@_gen_field_init
class OurDecimalField(fields.DecimalField, RendererMixin):
    pass

@_gen_field_init
class OurIntegerField(fields.IntegerField, RendererMixin):
    pass

@_gen_field_init
class OurBooleanField(fields.BooleanField, RendererMixin):
    pass

@_gen_field_init
class OurDecimalField(fields.DecimalField, RendererMixin):
    pass

@_gen_field_init
class NullableTextField(OurTextField):
    def process_formdata(self, valuelist):
        super(NullableTextField, self).process_formdata(valuelist)
        if self.data == '':
            self.data = None
