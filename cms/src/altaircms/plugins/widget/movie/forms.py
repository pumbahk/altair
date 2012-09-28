# -*- coding:utf-8 -*-
import wtforms.form as form
import wtforms.fields as fields
import wtforms.validators as validators


class MovieInfoForm(form.Form):
    width = fields.TextField(id="width", label=u"レンダリングのwidth")
    height = fields.TextField(id="height", label=u"レンダリング時のheight")
    alt = fields.TextField(id="alt", label=u"レンダリング時のalt")
