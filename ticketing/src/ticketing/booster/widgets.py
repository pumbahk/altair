from wtforms.widgets import HTMLString, ListWidget
import re

__all__ = (
    'GenericSerializerWidget',
    'Serializer',
    )

class GenericSerializerWidget(object):
    def __init__(self, delimiter='', head='', tail='', prologue='', epilogue='', separator='', prefix_label=True):
        self.delimiter = delimiter
        self.head = head
        self.tail = tail

    def __call__(self, field, **kwargs):
        html = []
        html.append(self.prologue)
        first = True
        for subfield in field:
            if not first:
                html.append(self.delimiter)
            html.append(self.head)
            if self.prefix_label:
                html.append(subfield.label)
                html.append(self.separator)
                html.append(subfield())
            else:
                html.append(subfield())
                html.append(self.separator)
                html.append(subfield.label)
            html.append(self.tail)
            first = False
        html.append(self.epilogue)
        return HTMLString(''.join(html))

class Switcher(object):
    def __init__(self, default, **widgets):
        self.default = default
        self.widgets = widgets

    def __call__(self, field, *args, **kwargs):
        widget = kwargs.get('widget') or self.default
        _kwargs = dict()
        for k, v in kwargs.items():
            g = re.match(r'_(.*)_([^_]*)$', k)
            if g is not None:
                if g.group(1) == widget:
                  _kwargs[g.group(2)] = v
            elif k != 'widget':
                _kwargs[k] = v
        return self.widgets[kwargs.get('widget') or self.default](field, *args, **_kwargs)
