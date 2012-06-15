# -*- coding:utf-8 -*-
import wtforms.form as form
import wtforms.fields as fields
import wtforms.validators as validators


class ImageInfoForm(form.Form):
    href = fields.TextField(id="href", label=u"リンク先")
    width = fields.TextField(id="width", label=u"レンダリングのwidth")
    height = fields.TextField(id="height", label=u"レンダリング時のheight")
    alt = fields.TextField(id="alt", label=u"レンダリング時のalt")
