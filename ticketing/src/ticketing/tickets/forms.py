# -*- coding: utf-8 -*-

import json
import os.path
from StringIO import StringIO
import xml.etree.ElementTree as etree
from wtforms import Form
from wtforms import TextField, IntegerField, HiddenField, SelectField, SelectMultipleField, FileField
from wtforms.validators import Regexp, Length, Optional, ValidationError, StopValidation
from wtforms.widgets import TextArea
from ticketing.formhelpers import DateTimeField, Translations, Required
from ticketing.core.models import Event, Account, DeliveryMethod
from .models import TicketFormat

class FileRequired(object):
    def __init__(self, extnames=None):
        self.extnames = extnames

    field_flags = ('required', )

    def __call__(self, form, field):
        if not hasattr(field.data, "filename") or not field.data.filename:
            raise StopValidation(u"ファイルが存在しません。アップロードするファイルを指定してください")
        
        if self.extnames and not os.path.splitext(field.data.filename)[1] in self.extnames:
            raise StopValidation(u"対応していないファイル形式です。(対応している形式: %s)" % self.extnames)

    def none_is_ok(self, form, field):
        if not field.data:
            return None
        else:
            return self.__call__(form, field)

def build_template_data_value(drawing):
    if drawing:
        out = StringIO()
        drawing.write(out) #doc declaration?
        return dict(drawing=out.getvalue())
    return dict()
    
class TicketTemplateForm(Form):
    def _get_translations(self):
        return Translations()

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata=formdata, obj=obj, prefix=prefix, **kwargs)
        if 'organization_id' in kwargs:
            self.ticket_format.choices = [
                (format.id, format.name) for format in TicketFormat.filter_by(organization_id=kwargs['organization_id'])
            ]
        self._drawing = None

    name = TextField(
        label = u'名前',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )

    ticket_format = SelectField(
        label=u"チケット様式",
        choices=[], 
        coerce=long , 
        validators=[Required()]
    )

    drawing = FileField(
        label=u"券面データ", 
        validators=[
            FileRequired([".xml", ".svg"])
        ]
     )    

    def validate_drawing(form, field):
        try:
            form._drawing = etree.parse(field.data.file)
            field.data.file.seek(0)
            return field.data
        except Exception, e:
            raise ValidationError(str(e))

    def validate(self):
        super(type(self), self).validate()
        self.data_value = build_template_data_value(self._drawing)
        return not bool(self.errors)

class TicketTemplateEditForm(Form):
    def _get_translations(self):
        return Translations()

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata=formdata, obj=obj, prefix=prefix, **kwargs)
        if 'organization_id' in kwargs:
            self.ticket_format.choices = [
                (format.id, format.name) for format in TicketFormat.filter_by(organization_id=kwargs['organization_id'])
            ]
        self._drawing = None

    name = TextField(
        label = u'名前',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )

    ticket_format = SelectField(
        label=u"チケット様式",
        choices=[], 
        coerce=long , 
        validators=[Required()]
    )

    drawing = FileField(
        label=u"券面データ", 
        validators=[
            FileRequired([".xml", ".svg"]).none_is_ok
        ]
     )    

    def validate_drawing(form, field):
        if not field.data and not hasattr(field.data, "file"):
            return None
        try:
            form._drawing = etree.parse(field.data.file)
            field.data.file.seek(0)
            return field.data
        except Exception, e:
            raise ValidationError(str(e))

    def validate(self):
        super(type(self), self).validate()
        self.data_value = build_template_data_value(self._drawing)
        return not bool(self.errors)
        

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

    delivery_methods = SelectMultipleField(
        label=u"配送方法",
        validators=[Required()], 
        coerce=long , 
        choices=[])
    
    def validate_data_value(form, field):
        try:
            data = json.loads(field.data)
            form.data["data_value"] = data
            if not "size" in data:
                raise ValidationError("size is not found")
            if not data["size"].get("width"):
                raise ValidationError("size[\"width\"] is not found")
            if not data["size"].get("height"):
                raise ValidationError("size[\"height\"] is not found")

            if not "perforations" in data:
                raise ValidationError("perforations is not found")
            if not "printable_areas" in data:
                raise ValidationError("printable_areas is not found")
            
        except Exception, e:
            raise ValidationError(str(e))
