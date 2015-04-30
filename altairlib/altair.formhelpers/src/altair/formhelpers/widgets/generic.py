from cgi import escape
import json
from wtforms.widgets.core import Input
from .input import InputRendrant, OurInput
from .select import OurSelectWidget
from .context import Rendrant

class HiddenMultipleSelectRendrant(Rendrant):
    def __init__(self, field, html, id_list):
        super(HiddenMultipleSelectRendrant, self).__init__(field, html)
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
        retval.push(n.value);
      }
      return retval;
    },
    getUIElements: function() {
      return ns;
    }
  });
})(%(name)s, %(id_list)s);
</script>''' % dict(name=json.dumps(self.field.short_name), id_list=json.dumps(self.id_list), registry_var_name=json.dumps(registry_var_name))

class GenericHiddenInput(Input):
    def _render_multiple(self, field, **kwargs):
        from ..fields import PHPCompatibleSelectMultipleField
        html = []
        if isinstance(field, PHPCompatibleSelectMultipleField):
            name = field.name + u'[]'
        else:
            name = field.name

        outer_box_id = kwargs.pop('id', field.id)
        id_prefix = kwargs.pop('id_prefix', outer_box_id)
        id_list = []
        kwargs.pop('context', None)
        for i, (val, label, selected) in enumerate(field.iter_choices()):
            id = id_prefix + u'.' + str(i)
            if selected:
                id_list.append(id)
                html.append(
                    u'<input type="hidden" id="%(id)s" name="%(name)s" value="%(value)s" />' % dict(
                        id=escape(id),
                        name=escape(name),
                        value=escape(val)
                        )
                    )
        return HiddenMultipleSelectRendrant(field, u''.join(html), id_list)

    def _render_value(self, field, **kwargs):
        password = kwargs.pop('password', False)
        js_coercer = getattr(field, 'build_js_coercer', None)
        if js_coercer is not None:
            js_coercer = js_coercer()
        else:
            js_coercer = u'function (v) { return v; }'
        return InputRendrant(
            field,
            u'<input type="hidden" id="%(id)s" name="%(name)s" value="%(value)s" />' % dict(
                id=escape(field.id),
                name=escape(field.name),
                value=escape(u"" if password else field._value())
                ),
            field.id,
            js_coercer
            )

    def __call__(self, field, **kwargs):
        if hasattr(field, '_value'):
            return self._render_value(field, **kwargs)
        else:
            return self._render_multiple(field, **kwargs)
