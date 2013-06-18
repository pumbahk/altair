import re

__all__ = [
    'Switcher',
    ]

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

