# -*- coding: utf-8 -*-

from altair.formhelpers.form import OurForm
from wtforms import TextField, IntegerField
from wtforms.validators import Length
from altair.formhelpers import Required


class SkidataPropertyForm(OurForm):
    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        super(SkidataPropertyForm, self).__init__(formdata=formdata, obj=obj, prefix=prefix, **kwargs)
        if 'skidata_property' in kwargs:
            self.name.data = kwargs['skidata_property'].name
            self.value.data = kwargs['skidata_property'].value

    name = TextField(
        label=u'プロパティ名',
        validators=[
            Required(message=u'文字列を入力してください'),
            Length(max=30, message=u'30文字以内で入力してください'),
        ]
    )

    value = IntegerField(
        label=u'プロパティ値(数値)',
        validators=[Required(message=u'数値を入力してください')]
    )
