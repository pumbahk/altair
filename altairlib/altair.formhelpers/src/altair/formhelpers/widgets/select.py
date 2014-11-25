# encoding: utf-8

# https://gist.github.com/playpauseandstop/1590178

import json
from wtforms.fields import SelectField as BaseSelectField
from wtforms.validators import ValidationError
from wtforms.widgets import HTMLString, html_params
from cgi import escape
from wtforms.widgets import Select as BaseSelectWidget
from wtforms.compat import text_type
from zope.deprecation import deprecate
from .context import Rendrant

__all__ = [
    'OurSelectWidget',
    'GroupedSelect',
    'SelectField',
    'SelectWidget',
    ]


class SelectRendrant(Rendrant):
    def __init__(self, field, html, id_, coercer):
        super(SelectRendrant, self).__init__(field, html)
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


class OurSelectWidget(BaseSelectWidget):
    @classmethod
    def render_option(cls, value, label, selected, **kwargs):
        kwargs.pop('context', None)
        options = dict(kwargs, value=value)
        label_html = None
        if hasattr(label, '__html__'):
            label_html = label.__html__()
        elif isinstance(label, basestring):
            label_html = escape(text_type(label))
        if selected:
            options['selected'] = u'selected'
        return HTMLString(u'<option %s>%s</option>' % (html_params(**options), label_html))

    def __call__(self, field, **kwargs):
        kwargs.pop('context', None)
        js_coercer = getattr(field, 'build_js_coercer', None)
        if js_coercer is not None:
            js_coercer = js_coercer()
        else:
            js_coercer = u'function (v) { return v; }'
        return SelectRendrant(
            field,
            super(OurSelectWidget, self).__call__(field, **kwargs),
            field.id,
            js_coercer
            )

class GroupedSelect(OurSelectWidget):
    def render_group(self, group_name, group):
        html = [u'<optgroup label="%s">' % group_name]
        for value, label, selected in group:
            html.append(self.render_option(value, label, selected))
        html.append(u'</optgroup>')
        return HTMLString(u''.join(html))

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.pop('context', None)
        if self.multiple:
            kwargs['multiple'] = True
        html = ['<select %s>' % html_params(name=field.name, **kwargs)]
        for group_name, group in field.iter_choice_groups():
            if group_name is not None:
                html.append(self.render_group(group_name, group))
            else:
                for value, label, selected in group:
                    html.append(self.render_option(value, label, selected))
        html.append('</select>')
        js_coercer = getattr(field, 'build_js_coercer', None)
        if js_coercer is not None:
            js_coercer = js_coercer()
        else:
            js_coercer = u'function (v) { return v; }'
        return SelectRendrant(
            field,
            u''.join(html),
            field.id,
            js_coercer
            )


@deprecate
class SelectWidget(BaseSelectWidget):
    """
    Add support of choices with ``optgroup`` to the ``Select`` widget.
    """
    @classmethod
    def render_option(cls, value, label, selected):
        """
        Render option as HTML tag, but not forget to wrap options into
        ``optgroup`` tag if ``label`` var is ``list`` or ``tuple``.
        """
        kwargs.pop('context', None)
        label_html = None
        if hasattr(label, '__html__'):
            label_html = label.__html__()
        elif isinstance(label, basestring):
            label_html = escape(text_type(label))
        if label_html is not None:
            options = {'value': value}

            if selected:
                options['selected'] = u'selected'

            html = u'<option %s>%s</option>'
            data = (html_params(**options), label_html)
        else:
            children = []

            for item_value, item_label in label:
                item_html = cls.render_option(item_value, item_label, selected)
                children.append(item_html)

            html = u'<optgroup label="%s">%s</optgroup>'
            data = (escape(unicode(value)), u'\n'.join(children))
        return HTMLString(html % data)

@deprecate
class SelectField(BaseSelectField):
    """
    Add support of ``optgorup``'s' to default WTForms' ``SelectField`` class.

    So, next choices would be supported as well::

        (
            ('Fruits', (
                ('apple', 'Apple'),
                ('peach', 'Peach'),
                ('pear', 'Pear')
            )),
            ('Vegetables', (
                ('cucumber', 'Cucumber'),
                ('potato', 'Potato'),
                ('tomato', 'Tomato'),
            ))
        )

    """

    def pre_validate(self, form, choices=None):
        """
        Don't forget to validate also values from embedded lists.
        """
        default_choices = choices is None
        choices = choices or self.choices

        for value, label in choices:
            found = False

            if isinstance(label, (list, tuple)):
                found = self.pre_validate(form, label)

            if found or value == self.data:
                return True

        if not default_choices:
            return False

        raise ValidationError(self.gettext(u'Not a valid choice'))

class BooleanSelect(object):
    def __init__(self, choices):
        if len(choices) != 2:
            raise ValueError('len(choices) must be 2')
        self.choices = choices

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.pop('context', None)
        html = ['<select %s>' % html_params(name=field.name, **kwargs)]
        for v, label in enumerate(self.choices):
            v = bool(v)
            sv = u'1' if v else u''
            html.append(self.render_option(sv, label, v == bool(field.data)))
        html.append('</select>')
        return HTMLString(''.join(html))

    @classmethod
    def render_option(cls, value, label, selected, **kwargs):
        options = dict(kwargs, value=value)
        if selected:
            options['selected'] = True
        if hasattr(label, '__html__'):
            label_html = label.__html__()
        else:
            label_html = escape(text_type(label))
        return HTMLString('<option %s>%s</option>' % (html_params(**options), label_html))
