# -*- coding:utf-8 -*-
import wtforms.form as form
import wtforms.fields as fields
import wtforms.validators as validators


class ImageInfoForm(form.Form):
    href = fields.TextField(id="href", label=u"リンク先")

    
