# -*- coding: utf-8 -*-

import json
import os.path
from StringIO import StringIO
from lxml import etree
#import xml.etree.ElementTree as etree
from wtforms import Form
from wtforms import TextField, IntegerField, HiddenField, SelectField, SelectMultipleField, FileField
from wtforms.validators import Regexp, Length, Optional, ValidationError, StopValidation
from wtforms.widgets import TextArea
from ticketing.formhelpers import DateTimeField, Translations, Required
from ticketing.core.models import Event, Account, DeliveryMethod
from ticketing.core.models import TicketFormat
from .convert import to_opcodes
from .cleaner import cleanup_svg

def filestorage_has_file(storage):
    return hasattr(storage, "filename") and storage.file

class FileRequired(object):
    def __init__(self, extnames=None):
        self.extnames = extnames

    field_flags = ('required', )

    def __call__(self, form, field):
        if not filestorage_has_file(field.data):
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
        drawing.write(out, encoding="UTF-8") #doc declaration?
        return dict(drawing=out.getvalue())
    return dict()

def get_validated_xmltree_as_opcode_source(svgio):
    try:
        xmltree = etree.parse(svgio)
        cleanup_svg(xmltree)
    except Exception, e:
        raise ValidationError("xml:" + str(e))
    try:
        to_opcodes(xmltree)
        svgio.seek(0)
        return xmltree
    except Exception, e:
        raise ValidationError("opcode:" + str(e))

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
        form._drawing = get_validated_xmltree_as_opcode_source(field.data.file)
        return field.data

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
        if not filestorage_has_file(field.data):
            return None
        form._drawing = get_validated_xmltree_as_opcode_source(field.data.file)
        return field.data

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
            if not "print_offset" in data:
                raise ValidationError("printable_offset is not found")
            
        except Exception, e:
            raise ValidationError(str(e))
