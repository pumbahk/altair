from wtforms.widgets.core import HTMLString, html_params
from cgi import escape

__all__ = (
    'CheckboxMultipleSelect',
    )

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
            if selected:
                kwargs['checked'] = "checked"
            else:
                kwargs.pop('checked', None)
            html.extend([
                '<span %s>' % html_params(class_='checkbox-set-item'),
                '<input %s />' % html_params(id=id, type=input_type, name=name,  value=val, **kwargs),
                ' ',
                '<label %s>%s</label>' % (
                    html_params(for_=id),
                    escape(label)
                    ),
                '</span>',
                ])
        html.append('</div>')
        return HTMLString(''.join(html))

