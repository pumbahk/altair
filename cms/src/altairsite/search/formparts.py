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
