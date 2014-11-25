from wtforms.widgets.core import HTMLString, html_params
from cgi import escape
import json
from .list import first_last_iter, update_classes
from .context import Rendrant

__all__ = (
    'CheckboxMultipleSelect',
    'LabelledCheckboxInput',
    'LabelledRadioInput',
    )

def render_checkbox(input_type, id, name, val, label, selected, label_class, **kwargs):
    if selected:
        kwargs['checked'] = "checked"
    else:
        kwargs.pop('checked', None)

    label_attrs = {}
    if label_class is not None:
        label_attrs['class_'] = label_class

    html = [
        u'<label %s>' % html_params(for_=id, **label_attrs),
        u'<input %s />' % html_params(id=id, type=input_type, name=name, value=val, **kwargs),
        u' ',
        escape(label),
        u'</label>',
        ]
    return HTMLString(''.join(html))


class CheckboxMultipleSelectRendrant(Rendrant):
    def __init__(self, field, html, id_list):
        super(CheckboxMultipleSelectRendrant, self).__init__(field, html)
        self.id_list = id_list

    def render_js_data_provider(self, registry_var_name):
        return u'''<script type="text/javascript">
(function(name, id_list) {
  var ns = [];
  for (var i = 0; i < id_list.length; i++) {
    var n = document.getElementById(id_list[i]);
    ns.push(n);
  }
  window[%(registry_var_name)s].registerProvider(name, {
    getValue: function () {
      var retval = [];
      for (var i = 0; i < ns.length; i++) {
        var n = ns[i];
        if (n.checked) retval.push(n.value);
      }
      return retval;
    },
    getUIElements: function () {
      return ns;
    }
  });
})(%(name)s, %(id_list)s);
</script>''' % dict(name=json.dumps(self.field.short_name), id_list=json.dumps(self.id_list), registry_var_name=json.dumps(registry_var_name))


class CheckboxMultipleSelect(object):
    def __init__(self, multiple=False, outer_html_tag='div', inner_html_tag=None, inner_html_pre='', inner_html_post='', inner_tag_classes=None, first_inner_tag_classes=None, last_inner_tag_classes=None):
        self.multiple = multiple
        self.outer_html_tag = outer_html_tag
        self.inner_html_tag = inner_html_tag
        self.inner_html_pre = inner_html_pre
        self.inner_html_post = inner_html_post
        self.inner_tag_classes = inner_tag_classes
        self.first_inner_tag_classes = first_inner_tag_classes
        self.last_inner_tag_classes = last_inner_tag_classes

    def __call__(self, field, **kwargs):
        from ..fields import PHPCompatibleSelectMultipleField
        html = []
        if self.multiple:
            input_type = u'checkbox'
            if isinstance(field, PHPCompatibleSelectMultipleField):
                name = field.name + u'[]'
            else:
                name = field.name
        else:
            input_type = u'radio'
            name = field.name

        outer_box_id = kwargs.pop('id', field.id)
        id_prefix = kwargs.pop('id_prefix', outer_box_id)
        html.append(u'<%s %s>' % (self.outer_html_tag, html_params(id=outer_box_id, class_=u'checkbox-set')))
        id_list = []
        kwargs.pop('context', None)
        for i, (first, last, (val, label, selected)) in enumerate(first_last_iter(field.iter_choices())):
            if self.inner_html_tag:
                html.append(u'<%s' % self.inner_html_tag)
                inner_tag_classes = []
                update_classes(inner_tag_classes, self.inner_tag_classes)
                if first:
                    update_classes(inner_tag_classes, self.first_inner_tag_classes)
                if last:
                    update_classes(inner_tag_classes, self.last_inner_tag_classes)
                if inner_tag_classes:
                    params = html_params(class_=' '.join(inner_tag_classes))
                else:
                    params = None
                if params:
                    html.append(u' ')
                    html.append(params)
                html.append(u'>')
            if self.inner_html_pre:
                html.append(self.inner_html_pre)
            id = id_prefix + u'.' + str(i)
            html.append(render_checkbox(u'checkbox', id, name, val, label, selected, u'checkbox-set-item', **kwargs))
            if self.inner_html_post:
                html.append(self.inner_html_post)
            if self.inner_html_tag:
                html.append('</%s>' % self.inner_html_tag)
            id_list.append(id)
        html.append(u'</%s>' % self.outer_html_tag)
        return CheckboxMultipleSelectRendrant(field, u''.join(html), id_list)


class LabelledCheckboxInputRendrant(Rendrant):
    def __init__(self, field, html, id_):
        super(LabelledCheckboxInputRendrant, self).__init__(field, html)
        self.id = id_

    def render_js_data_provider(self, registry_var_name):
        return u'''<script type="text/javascript">
(function(name, id) {
  var n = document.getElementById(id);
  window[%(registry_var_name)s].registerProvider(name, {
    getValue: function () {
      return n.checked ? n.value: null;
    },
    getUIElements: function () {
      return [n];
    }
  });
})({name}, {id});
</script>'''.format(name=json.dumps(self.field.short_name), id=json.dumps(self.id), registry_var_name=json.dumps(registry_var_name))

class LabelledCheckboxInputBase(object):
    def __call__(self, field, **kwargs):
        id = kwargs.pop('id', field.id)
        kwargs.pop('context', None)
        return LabelledCheckboxInputRendrant(
            field,
            render_checkbox(
                input_type=self.input_type,
                id=id,
                name=field.name,
                val=field._value(),
                label=field.label.text,
                selected=bool(field.data),
                label_class=kwargs.pop('label_class', None),
                **kwargs
                ),
            id
            )

class LabelledCheckboxInput(LabelledCheckboxInputBase):
    input_type = u'checkbox'

class LabelledRadioInput(LabelledCheckboxInputBase):
    input_type = u'radio'
