import re
import json
from wtforms.widgets.core import html_params
from .context import Rendrant

__all__ = (
    'OurListWidget',
    'OurTableWidget',
    )

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

class ListRendrant(Rendrant):
    def __init__(self, field, html, id_, subfield_ids, coercer):
        super(ListRendrant, self).__init__(field, html)
        self.id = id_
        self.subfield_ids = subfield_ids
        self.coercer = coercer

    def render_js_data_provider(self, registry_var_name):
        return u'''<script type="text/javascript">
(function(name, id, subfieldIds, coercer) {
  var n = [];
  for (var i = 0; i < subfieldIds.length; i++) {
    n.push(document.getElementById(subfieldIds[i]));
  }
  window[%(registry_var_name)s].registerProvider(name, {
    getValue: function () {
      var v = null;
      for (var i = 0; i < n.length; i++) {
        if (n[i].checked)
          v = n[i].value;
      }
      return coercer(v);
    },
    getUIElements: function() {
      return n;
    }
  });
})(%(name)s, %(id)s, %(subfield_ids)s, %(coercer)s);
</script>''' % dict(name=json.dumps(self.field.short_name), id=json.dumps(self.id), subfield_ids=json.dumps(self.subfield_ids), coercer=self.coercer, registry_var_name=json.dumps(registry_var_name))


def default_subfield_id_formatter(id_, subfield, i):
    return u'%s-%s-%d' % (id_, subfield.short_name, i)

class OurListWidget(object):
    def __init__(self, outer_html_tag='ul', inner_html_tag='li', inner_html_pre='', inner_html_post='', inner_tag_classes=None, first_inner_tag_classes=None, last_inner_tag_classes=None, prefix_label=True, rendrant_factory=None, subfield_id_formatter=None, omit_labels=False):
        if rendrant_factory is None:
            rendrant_factory = ListRendrant
        if subfield_id_formatter is None:
            subfield_id_formatter = default_subfield_id_formatter
        self.outer_html_tag = outer_html_tag
        self.inner_html_tag = inner_html_tag
        self.inner_html_pre = inner_html_pre
        self.inner_html_post = inner_html_post
        self.inner_tag_classes = inner_tag_classes
        self.first_inner_tag_classes = first_inner_tag_classes
        self.last_inner_tag_classes = last_inner_tag_classes
        self.prefix_label = prefix_label
        self.rendrant_factory = rendrant_factory
        self.subfield_id_formatter = subfield_id_formatter
        self.omit_labels = omit_labels

    def __call__(self, field, **kwargs):
        id_ = kwargs.setdefault('id', field.id)
        kwargs.pop('context', None)
        html = []
        subfield_ids = [];
        if self.outer_html_tag:
            html.append('<%s %s>' % (self.outer_html_tag, html_params(**kwargs)))

        for i, (first, last, subfield) in enumerate(first_last_iter(field)):
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
            subfield_id = self.subfield_id_formatter(id_, subfield, i)
            subfield_html = subfield(id=subfield_id)
            if subfield.label and not self.omit_labels:
                if self.prefix_label:
                    html.append('%s: %s' % (subfield.label(field_id=subfield_id), subfield_html))
                else:
                    html.append('%s %s' % (subfield_html, subfield.label(field_id=subfield_id)))
            else:
                html.append(subfield_html)
            if self.inner_html_post:
                html.append(self.inner_html_post)
            if self.inner_html_tag:
                html.append('</%s>' % self.inner_html_tag)
            subfield_ids.append(subfield_id)
        if self.outer_html_tag:
            html.append('</%s>' % self.outer_html_tag)
        return self.rendrant_factory(field, ''.join(html), id_, subfield_ids, u'function (v) { return v; }')

class OurTableWidget(object):
    def __init__(self, outer_html_tag=True, inner_html_tag=u'tr', inner_html_label_tag=u'th', inner_html_field_tag=u'td', inner_html_label_pre='', inner_html_label_post='', inner_html_field_pre='', inner_html_field_post='', inner_tag_classes=None, first_inner_tag_classes=None, last_inner_tag_classes=None, rendrant_factory=None, subfield_id_formatter=None):
        if rendrant_factory is None:
            rendrant_factory = ListRendrant
        if subfield_id_formatter is None:
            subfield_id_formatter = default_subfield_id_formatter
        if outer_html_tag is True:
            outer_html_tag = u'table'
        elif outer_html_tag is False:
            outer_html_tag = u''
        self.outer_html_tag = outer_html_tag
        self.inner_html_tag = inner_html_tag
        self.inner_html_label_tag = inner_html_label_tag
        self.inner_html_field_tag = inner_html_field_tag
        self.inner_html_label_pre = inner_html_label_pre
        self.inner_html_label_post = inner_html_label_post
        self.inner_html_field_pre = inner_html_field_pre
        self.inner_html_field_post = inner_html_field_post
        self.inner_tag_classes = inner_tag_classes
        self.first_inner_tag_classes = first_inner_tag_classes
        self.last_inner_tag_classes = last_inner_tag_classes
        self.rendrant_factory = rendrant_factory
        self.subfield_id_formatter = subfield_id_formatter

    def __call__(self, field, **kwargs):
        id_ = kwargs.setdefault('id', field.id)
        kwargs.pop('context', None)
        html = []
        subfield_ids = [];
        if self.outer_html_tag:
            html.append('<%s %s>' % (self.outer_html_tag, html_params(**kwargs)))

        for i, (first, last, subfield) in enumerate(first_last_iter(field)):
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

            subfield_id = self.subfield_id_formatter(id_, subfield, i)
            subfield_html = subfield(id=subfield_id)

            html.append('<%s>' % self.inner_html_label_tag)
            if self.inner_html_label_pre:
                html.append(self.inner_html_label_pre)
            html.append(subfield.label(for_=subfield_id))
            if self.inner_html_label_post:
                html.append(self.inner_html_label_post)
            html.append('</%s>' % self.inner_html_label_tag)

            html.append('<%s>' % self.inner_html_field_tag)
            if self.inner_html_field_pre:
                html.append(self.inner_html_field_pre)
            html.append(subfield_html)
            if self.inner_html_field_post:
                html.append(self.inner_html_field_post)
            html.append('</%s>' % self.inner_html_field_tag)

            if self.inner_html_tag:
                html.append('</%s>' % self.inner_html_tag)
            subfield_ids.append(subfield_id)
        if self.outer_html_tag:
            html.append('</%s>' % self.outer_html_tag)
        return self.rendrant_factory(field, ''.join(html), id_, subfield_ids, u'function (v) { return v; }')


