from wtforms.widgets.core import HTMLString, html_params
from cgi import escape

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
    def __init__(self, multiple=False):
        self.multiple = multiple

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
        html.append('<div %s>' % html_params(id=outer_box_id, class_='checkbox-set'))
        for i, (val, label, selected) in enumerate(field.iter_choices()):
            id = id_prefix + '.' + str(i)
            html.append(render_checkbox('checkbox', id, name, val, label, selected, 'checkbox-set-item', **kwargs))
        html.append('</div>')
        return HTMLString(''.join(html))

class LabelledCheckboxInputBase(object):
    def __call__(self, field, **kwargs):
        id = kwargs.pop('id', field.id)
        return render_checkbox(self.input_type, id, field.name, field._value(), field.label.text, bool(field.data), kwargs.pop('label_class', None), **kwargs)

class LabelledCheckboxInput(LabelledCheckboxInputBase):
    input_type = 'checkbox'

class LabelledRadioInput(LabelledCheckboxInputBase):
    input_type = 'radio'
