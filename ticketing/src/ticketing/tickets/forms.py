# -*- coding: utf-8 -*-

import json
from wtforms import Form
from wtforms import TextField, IntegerField, HiddenField, SelectField, SelectMultipleField
from wtforms.validators import Regexp, Length, Optional, ValidationError
from wtforms.widgets import TextArea
from ticketing.formhelpers import DateTimeField, Translations, Required
from ticketing.core.models import Event, Account, DeliveryMethod

class TicketFormatForm(Form):
    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        # super(type(self), self).__init__(self, formdata=formdata, obj=obj, prefix=prefix, **kwargs)
        Form.__init__(self, formdata=formdata, obj=obj, prefix=prefix, **kwargs)
        if 'organization_id' in kwargs:
            self.delivery_methods.choices = [
                (dmethod.id, dmethod.name) for dmethod in DeliveryMethod.filter_by(organization_id=kwargs['organization_id'])
            ]

    def _get_translations(self):
        return Translations()

    name = TextField(
        label = u'名前',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )

    data_value = TextField(
        label = u"データ", 
        validators=[
            Required(), 
            ## json?
            ], 
        widget=TextArea()
        )

    delivery_methods = SelectMultipleField(label=u"配送方法", choices=[])
    
    def validate_data_value(form, field):
        try:
            data = json.loads(field.data)
            form.data["data_value"] = data
            if not "size" in data:
                raise ValidationError("size is not found")
            if not "perforations" in data:
                raise ValidationError("perforations is not found")
            if not "printable_areas" in data:
                raise ValidationError("printable_areas is not found")
            
        except Exception, e:
            raise ValidationError(str(e))

    def validate(self):
        super(type(self), self).validate()
        if "delivery_methods" in self.errors:
            del self.errors["delivery_methods"]
        return not bool(self.errors)
