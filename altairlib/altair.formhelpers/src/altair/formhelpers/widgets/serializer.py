from wtforms.widgets import HTMLString

__all__ = [
    'GenericSerializerWidget',
    ]

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
