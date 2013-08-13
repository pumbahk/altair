from wtforms import fields
from .select import LazySelectField, LazySelectMultipleField, LazyGroupedSelectField, LazyGroupedSelectMultipleField, PHPCompatibleSelectMultipleField

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

    def __init__(self, label=None, *args, **kwargs):
        _form  = kwargs.pop('_form', None)
        hide_on_new = kwargs.pop('hide_on_new', False)
        raw_input_filters = kwargs.pop('raw_input_filters', [])
        if callable(label):
            label = label()
        super(klass, self).__init__(label, *args, **kwargs)
        self.form = _form
        self.hide_on_new = hide_on_new
        self.raw_input_filters = raw_input_filters
        for base in self.__class__.__bases__[1:]:
            if hasattr(base, '__mixin_init__'):
                base.__mixin_init__(self, *args, **kwargs)

    def process_formdata(self, valuelist):
        for raw_input_filter in self.raw_input_filters:
            valuelist = raw_input_filter(valuelist)
        return super(type(self), self).process_formdata(valuelist)
 
    def __call__(self, *args, **kwargs):
        if hasattr(self, '_render'):
            return self._render(__callee=prev_call, *args, **kwargs)
        else:
            return prev_call(self, *args, **kwargs)
    klass.__init__ = __init__
    klass.__call__ = __call__
    return klass

@_gen_field_init
class OurField(fields.Field, RendererMixin):
    pass

@_gen_field_init
class OurRadioField(fields.RadioField, RendererMixin):
    pass

@_gen_field_init
class OurTextField(fields.TextField, RendererMixin):
    pass

@_gen_field_init
class OurSelectField(LazySelectField, RendererMixin):
    pass

@_gen_field_init
class OurSelectMultipleField(LazySelectMultipleField, RendererMixin):
    pass

@_gen_field_init
class OurPHPCompatibleSelectMultipleField(PHPCompatibleSelectMultipleField, RendererMixin):
    pass

@_gen_field_init
class OurGroupedSelectField(LazyGroupedSelectField, RendererMixin):
    pass

@_gen_field_init
class OurGroupedSelectMultipleField(LazyGroupedSelectMultipleField, RendererMixin):
    pass

@_gen_field_init
class OurDecimalField(fields.DecimalField, RendererMixin):
    pass

@_gen_field_init
class OurIntegerField(fields.IntegerField, RendererMixin):
    pass

@_gen_field_init
class OurFloatField(fields.FloatField, RendererMixin):
    pass

@_gen_field_init
class OurBooleanField(fields.BooleanField, RendererMixin):
    pass

@_gen_field_init
class OurDecimalField(fields.DecimalField, RendererMixin):
    pass

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
