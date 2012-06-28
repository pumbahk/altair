#-*- coding:utf-8 -*-
import re
from wtforms import fields
from wtforms import widgets

#### widgets
##
class CheckboxWithLabelInput(widgets.CheckboxInput):
    """ [checkbox] label-as-text """
    def __call__(self, field, **kwargs):
        return u"%s%s" % (super(CheckboxWithLabelInput, self).__call__(field, **kwargs), field.label.text)

class PutOnlyWidget(object):
    """
    [elt] [elt] [elt] [elt] [elt]
    """
    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        html = []
        for subfield in field:
            html.append(u'%s%s' % (subfield(), subfield.label.text))
        return widgets.core.HTMLString(u' '.join(html))

#### maybe select fields
##

class MaybeSelectField(fields.SelectField):
    NONE_VALUE = "''''"
    def __init__(self, null_label=u"------", **kwargs):
        if "choices" in kwargs:
            choices = [x for x in kwargs["choices"]]
        else:
            choices = []
        choices.insert(0, (self.NONE_VALUE, null_label))
        kwargs["choices"] = choices
        super(MaybeSelectField, self).__init__(**kwargs)
        self.null_label = null_label

    def _value(self):
        if self.data is None:
            return self.null_label
        super(MaybeSelectField, self)._value()

    def process_formdata(self, valuelist):
        if not valuelist:
            self.data = None
        elif valuelist[0] == self.NONE_VALUE:
            self.data = None
        else:
            super(MaybeSelectField, self).process_formdata(valuelist)

#### checkbox list
##
class CheckboxListWidget(widgets.Input):
    def _collect_checkbox_elt(self, kwargs):
        elts = []
        checked_box = kwargs["value"]

        for k, v in kwargs["choices"]:
            if k in checked_box:
                elts.append(u'<input checked type="checkbox" name="%s" value="y"/>%s' % (k, v))
            else:
                elts.append(u'<input type="checkbox" name="%s"/>%s' % (k, v))
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
            self._collected_candidats = [k for k in formdata if k in candidates and formdata.getlist(k)]
        else:
            self._collected_candidats = []
        super(CheckboxListField, self).process(formdata, data=data)

    def process_formdata(self, valuelist):
        """ collect y's checkbox and return dict

        !! this field doesn't receive selfname's data.(against a usually field class) !!

        request.POST: {"a":"y", "b":"y", "illegal-key":"illegal-value"}
        form's choices: [("a", "a"), ("b", "b"), ("c", "c")]
        
        proces then => 
          self.data = ["a", "b"]
        """
        self.data = self._collected_candidats
        # defaults = {k:False for k, _ in self.choices}
        # defaults.update(self._collected_candidats)
        # self.data = defaults

