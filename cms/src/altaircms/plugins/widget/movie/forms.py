# -*- coding:utf-8 -*-
from altaircms.formhelpers import Form
import wtforms.fields as fields
import wtforms.validators as validators


class MovieInfoForm(Form):
    width = fields.TextField(id="width", label=u"レンダリングのwidth")
    height = fields.TextField(id="height", label=u"レンダリング時のheight")
    alt = fields.TextField(id="alt", label=u"レンダリング時のalt")
