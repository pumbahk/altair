import json
from wtforms.widgets.core import Input, TextArea, html_params
from cgi import escape
from .context import Rendrant

class InputRendrant(Rendrant):
    def __init__(self, field, html, id_, coercer):
        super(InputRendrant, self).__init__(field, html)
        self.id = id_
        self.coercer = coercer

    def render_js_data_provider(self, registry_var_name):
        return u'''<script type="text/javascript">
(function(name, id, coercer) {
  var n = document.getElementById(id);
  window[%(registry_var_name)s].registerProvider(name, {
    getValue: function () {
      return coercer(n.value);
    },
    getUIElements: function() {
      return [n];
    }
  });
})(%(name)s, %(id)s, %(coercer)s);
</script>''' % dict(name=json.dumps(self.field.short_name), id=json.dumps(self.id), coercer=self.coercer, registry_var_name=json.dumps(registry_var_name))


class OurInput(Input):
    def __call__(self, field, **kwargs):
        placeholder = kwargs.get('placeholder', False)
        if isinstance(placeholder, bool):
            if placeholder:
                kwargs['placeholder'] = field.label.text
        elif placeholder is not None:
            kwargs['placeholder'] = placeholder
        js_coercer = getattr(field, 'build_js_coercer', None)
        if js_coercer is not None:
            js_coercer = js_coercer()
        else:
            js_coercer = u'function (v) { return v; }'
        id = kwargs.pop('id', None) or field.id
        kwargs.pop('context', None)
        return InputRendrant(
            field,
            super(OurInput, self).__call__(field, id=id, **kwargs),
            id,
            js_coercer
            )

class OurTextInput(OurInput):
    input_type = 'text'

class OurPasswordInput(OurInput):
    input_type = 'password'

class OurHiddenInput(OurInput):
    input_type = 'hidden'

class OurCheckboxInput(OurInput):
    input_type = 'checkbox'

    def __init__(self, *args, **kwargs):
        label = kwargs.pop('label', None)
        super(OurCheckboxInput, self).__init__(*args, **kwargs)
        self.label = label

    def __call__(self, field, **kwargs):
        if getattr(field, 'checked', field.data):
                    kwargs['checked'] = True
        js_coercer = getattr(field, 'build_js_coercer', None)
        if js_coercer is not None:
            js_coercer = js_coercer()
        else:
            js_coercer = u'function (v) { return v; }'
        kwargs.pop('context', None)
        label = kwargs.pop('label', self.label)
        id = kwargs.pop('id', None) or field.id
        html = super(OurInput, self).__call__(field, id=id, **kwargs)
        if label is not None:
            html = html + u'<label for="%s">%s</label>' % (escape(id), label)
        return InputRendrant(
            field,
            html,
            id,
            js_coercer
            )

class OurRadioInput(OurCheckboxInput):
    input_type = 'radio'

class OurFileInput(OurInput):
    input_type = 'file'

class OurTextArea(TextArea):
    def __call__(self, field, **kwargs):
        if 'placeholder' not in kwargs:
            kwargs['placeholder'] = field.label.text
        js_coercer = getattr(field, 'build_js_coercer', None)
        if js_coercer is not None:
            js_coercer = js_coercer()
        else:
            js_coercer = u'function (v) { return v; }'
        kwargs.pop('context', None)
        return InputRendrant(
            field,
            super(OurTextArea, self).__call__(field, **kwargs),
            field.id,
            js_coercer
            )

class OurSelectInput(OurInput):
    def __init__(self, choices, **kwargs):
        super(OurSelectInput, self).__init__(**kwargs)
        self.choices = choices

    def __call__(self, field, **kwargs):
        js_coercer = getattr(field, 'build_js_coercer', None)
        if js_coercer is not None:
            js_coercer = js_coercer()
        else:
            js_coercer = u'function (v) { return v; }'
        kwargs.pop('context', None)
        id_ = kwargs.pop('id', None) or field.id
        html = []
        html.append(u'<select %s>' % html_params(name=field.name, id=id_, **kwargs))
        for v, label in self.choices:
            html.append(u'<option value="%s"%s>%s</option>' % (escape(v), u' selected="selected"' if v == field._value() else u'', label))
        html.append(u'</select>')
        return InputRendrant(
            field,
            u''.join(html),
            id_,
            js_coercer
            )

