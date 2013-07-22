from wtforms.widgets.core import HTMLString, html_params
import re

def first_last_iter(iterable):
    i = iter(iterable)
    try:
        value = i.next()
    except StopIteration:
        return
    first = True
    for next in i:
        yield first, False, value
        value = next
        first = False
    yield first, True, value

def update_classes(dest, src):
    if isinstance(src, basestring):
        dest.extend(re.split(r'\s+', src))
    else:
        try:
            dest.extend(iter(src))
        except TypeError:
            pass

class OurListWidget(object):
    def __init__(self, outer_html_tag='ul', inner_html_tag='li', inner_html_pre='', inner_html_post='', inner_tag_classes=None, first_inner_tag_classes=None, last_inner_tag_classes=None, prefix_label=True):
        self.outer_html_tag = outer_html_tag
        self.inner_html_tag = inner_html_tag
        self.inner_html_pre = inner_html_pre
        self.inner_html_post = inner_html_post
        self.inner_tag_classes = inner_tag_classes
        self.first_inner_tag_classes = first_inner_tag_classes
        self.last_inner_tag_classes = last_inner_tag_classes
        self.prefix_label = prefix_label

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        html = []
        if self.outer_html_tag:
            html.append('<%s %s>' % (self.outer_html_tag, html_params(**kwargs)))

        for first, last, subfield in first_last_iter(field):
            if self.inner_html_tag:
                html.append('<%s' % self.inner_html_tag)
                inner_tag_classes = []
                update_classes(inner_tag_classes, self.inner_tag_classes)
                if first:
                    update_classes(inner_tag_classes, self.first_inner_tag_classes)
                if last:
                    update_classes(inner_tag_classes, self.last_inner_tag_classes)
                params = html_params(class_=' '.join(inner_tag_classes))
                if params:
                    html.append(' ')
                    html.append(params)
                html.append('>')
            if self.inner_html_pre:
                html.append(self.inner_html_pre)
            if self.prefix_label:
                html.append('%s: %s' % (subfield.label, subfield()))
            else:
                html.append('%s %s' % (subfield(), subfield.label))
            if self.inner_html_post:
                html.append(self.inner_html_post)
            if self.inner_html_tag:
                html.append('</%s>' % self.inner_html_tag)
        if self.outer_html_tag:
            html.append('</%s>' % self.outer_html_tag)
        return HTMLString(''.join(html))

