#-*- coding:utf-8 -*-
import re
from wtforms import fields
from wtforms import widgets


class CheckboxListWidget(widgets.Input):
    def _collect_checkbox_elt(self, kwargs):
        elts = []
        checked_box = kwargs["value"]

        for k, v in kwargs["choices"]:
            if k in checked_box:
                elts.append(u'<input checked type="checkbox" name="%s" value="y"/> %s' % (k, v))
            else:
                elts.append(u'<input type="checkbox" name="%s"/> %s' % (k, v))
        return elts

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        if 'value' not in kwargs:
            kwargs['value'] = field._value()

        if "choices" not in kwargs:
            kwargs["choices"] = getattr(field, "choices", [])

        checkbox_elts = self._collect_checkbox_elt(kwargs)

        ## choices is not used in html_params rendering 
        kwargs.pop("choices")
        return widgets.HTMLString(u'<div %s>%s</div>' % (self.html_params(**kwargs), u"\n".join(checkbox_elts)))

class CheckboxListField(fields.Field):
    widget = CheckboxListWidget() ## todo refactoring
    delimiter_rx = re.compile("[,\s]+")

    def __init__(self, choices=None, **kwargs):
        super(CheckboxListField, self).__init__(**kwargs)
        self.choices = choices or []

    def _value(self):
        """
        return [u"name0", u"name1", u"name2"]
        """
        if not self.data:
            return []

        if isinstance(self.data, basestring):
            return self.delimiter_rx.split(self.data)
        elif hasattr(self.data, "__iter__"):
            return [unicode(x) for x in self.data]
        else:
            return self.data
        
    def process(self, formdata, data=fields.core._unset_value):
        """@orverride: 
        """
        if formdata:
            candidates = dict(self.choices)
            self._collected_candidats = [(k,True) for k in formdata if k in candidates and formdata.getlist(k)]
        else:
            self._collected_candidats = []
        super(CheckboxListField, self).process(formdata, data=data)

    def process_formdata(self, valuelist):
        """ collect y's checkbox and return dict

        !! this field doesn't receive selfname's data.(against a usually field class) !!

        request.POST: {"a":"y", "b":"y"}
        form's choices: [("a", "a"), ("b", "b"), ("c", "c")]
        
        proces then => 
          self.data = {"a": True, "b": True,  "c": False}
        """
        defaults = {k:False for k, _ in self.choices}
        defaults.update(self._collected_candidats)
        self.data = defaults

