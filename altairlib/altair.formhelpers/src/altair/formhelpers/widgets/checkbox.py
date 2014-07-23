from wtforms.widgets.core import HTMLString, html_params
from cgi import escape
from .list import first_last_iter, update_classes

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
        '<label %s>' % html_params(for_=id, **label_attrs),
        '<input %s />' % html_params(id=id, type=input_type, name=name, value=val, **kwargs),
        ' ',
        escape(label),
        '</label>',
        ]
    return HTMLString(''.join(html))

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
            input_type = 'checkbox'
            if isinstance(field, PHPCompatibleSelectMultipleField):
                name = field.name + '[]'
            else:
                name = field.name
        else:
            input_type = 'radio'
            name = field.name

        outer_box_id = kwargs.pop('id', field.id)
        id_prefix = kwargs.pop('id_prefix', outer_box_id)
        html.append(u'<%s %s>' % (self.outer_html_tag, html_params(id=outer_box_id, class_='checkbox-set')))
        for i, (first, last, (val, label, selected)) in enumerate(first_last_iter(field.iter_choices())):
            if self.inner_html_tag:
                html.append('<%s' % self.inner_html_tag)
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
                    html.append(' ')
                    html.append(params)
                html.append('>')
            if self.inner_html_pre:
                html.append(self.inner_html_pre)
            id = id_prefix + '.' + str(i)
            html.append(render_checkbox('checkbox', id, name, val, label, selected, 'checkbox-set-item', **kwargs))
            if self.inner_html_post:
                html.append(self.inner_html_post)
            if self.inner_html_tag:
                html.append('</%s>' % self.inner_html_tag)
        html.append(u'</%s>' % self.outer_html_tag)
        return HTMLString(''.join(html))

class LabelledCheckboxInputBase(object):
    def __call__(self, field, **kwargs):
        id = kwargs.pop('id', field.id)
        return render_checkbox(self.input_type, id, field.name, field._value(), field.label.text, bool(field.data), kwargs.pop('label_class', None), **kwargs)

class LabelledCheckboxInput(LabelledCheckboxInputBase):
    input_type = 'checkbox'

class LabelledRadioInput(LabelledCheckboxInputBase):
    input_type = 'radio'
