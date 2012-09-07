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
from .convert import to_opcodes, as_user_unit
from .cleaner import cleanup_svg
from .constants import PAPERS, ORIENTATIONS

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


def validate_extent(key, data):
    width = data.get(u"width")
    height = data.get(u"height")
    if width is None:
        raise ValidationError("%s[\"width\"] is not found" % key)
    if height is None:
        raise ValidationError("%s[\"height\"] is not found" % key)
    try:
        as_user_unit(width)
    except Exception as e:
        raise ValidationError("%s[\"width\"] is bad-formatted (%s)" % (key, e.args[0]) )
    try:
        as_user_unit(height)
    except Exception as e:
        raise ValidationError("%s[\"height\"] is bad-formatted (%s)" % (key, e.args[0]) )

def validate_position(key, data):
    x = data.get(u"x")
    y = data.get(u"y")
    if x is None:
        raise ValidationError("%s[\"x\"] is not found" % key)
    if y is None:
        raise ValidationError("%s[\"y\"] is not found" % key)
    try:
        as_user_unit(x)
    except Exception as e:
        raise ValidationError("%s[\"x\"] is bad-formatted (%s)" % (key, e.args[0]))
    try:
        as_user_unit(y)
    except Exception as e:
        raise ValidationError("%s[\"y\"] is bad-formatted (%s)" % (key, e.args[0]))

def validate_rectangle(key, data):
    validate_extent(key, data)
    validate_position(key, data)

def validate_perforations(key, data):
    if type(data) is not dict:
        raise ValidationError("%s is not an object" % key)
    vertical = data.get(u'vertical')
    horizontal = data.get(u'horizontal')
    if vertical is None:
        raise ValidationError("%s[\"vertical\"] is not found" % key)
    if type(vertical) is not list:
        raise ValidationError("%s[\"vertical\"] is not an array" % key)
    for i, pos in enumerate(vertical):
        try:
            as_user_unit(pos)
        except Exception as e:
            raise ValidationError("%s[\"vertical\"][%d] is bad-formatted (%s)" % (key, i, e.args[0]))
        
    if horizontal is None:
        raise ValidationError("%s[\"horizontal\"] is not found" % key)
    if type(horizontal) is not list:
        raise ValidationError("%s[\"horizontal\"] is not an array" % key)
    for i, pos in enumerate(horizontal):
        try:
            as_user_unit(pos)
        except Exception as e:
            raise ValidationError("%s[\"horizontal\"][%d] is bad-formatted (%s)" % (key, i, e.args[0]))

def validate_margin(key, data):
    if type(data) is not dict:
        raise ValidationError("%s is not an object" % key)
    left = data.get(u'left')
    if left is None:
        raise ValidationError("%s[\"left\"] is not found" % key)
    top = data.get(u'top')
    if top is None:
        raise ValidationError("%s[\"top\"] is not found" % key)
    right = data.get(u'right')
    if right is None:
        raise ValidationError("%s[\"right\"] is not found" % key)
    bottom = data.get(u'bottom')
    if bottom is None:
        raise ValidationError("%s[\"bottom\"] is not found" % key)

    for k, pos in dict(left=left, top=top, right=right, bottom=bottom).items():
        try:
            as_user_unit(pos)
        except Exception as e:
            raise ValidationError("%s[\"%s\"] is bad-formatted (%s)" % (key, k, e.args[0]))

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

    @staticmethod
    def _validate_ticket_section(data):
        size = data.get(u'size')
        printable_areas = data.get(u'printable_areas')
        print_offset = data.get(u'print_offset')
        perforations = data.get(u'perforations')
        if size is None:
            raise ValidationError("size is not found")
        validate_extent(u'size', size)
        if printable_areas is None:
            raise ValidationError("printable_areas is not found")
        if type(printable_areas) is not list:
            raise ValidationError("printable_areas is not an array")
        for i, printable_area in enumerate(printable_areas):
            validate_rectangle(u'printable_area[%d]' % i, printable_area)
        if print_offset is None:
            raise ValidationError("print_offset is not found")
        validate_position(u'print_offset', print_offset)
        validate_perforations(u'perforations', perforations) 

    @staticmethod
    def validate_data_value(form, field):
        try:
            data = json.loads(field.data)
            form.data["data_value"] = data
            TicketFormatForm._validate_ticket_section(data)
        except ValidationError:
            raise

class PageFormatForm(Form):
    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata=formdata, obj=obj, prefix=prefix, **kwargs)

    def _get_translations(self):
        return Translations()

    name = TextField(
        label = u'名前',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )

    printer_name = TextField(
        label = u'デフォルトのプリンタ名',
        validators=[
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

    @staticmethod
    def _validate_page_section(data):
        size = data.get(u'size')
        paper = data.get(u'paper')
        orientation = data.get(u'orientation')
        printable_area = data.get(u'printable_area')
        perforations = data.get(u'perforations')
        ticket_margin = data.get(u'ticket_margin')
        if size is None:
            raise ValidationError("size is not found")
        validate_extent(u'size', size)
        if paper is not None:
            if not paper in PAPERS:
                raise ValidationError("paper must be any of %s, got %s" % (u', '.join(PAPERS), paper))
        if orientation is None:
            raise ValidationError("orientation is not found")
        if not orientation in ORIENTATIONS:
            raise ValidationError("orientation must be either \"landscape\" or \"portrait\"")
        if printable_area is None:
            raise ValidationError("printable_area is not found")
        validate_rectangle(u'printable_area', printable_area)
        if ticket_margin is None:
            raise ValidationError("ticket_margin is not found")
        validate_margin(u'ticket_margin', ticket_margin)
        validate_perforations(u'perforations', perforations)

    @staticmethod
    def validate_data_value(form, field):
        try:
            data = json.loads(field.data)
            form.data["data_value"] = data
            PageFormatForm._validate_page_section(data)
        except ValidationError:
            raise
