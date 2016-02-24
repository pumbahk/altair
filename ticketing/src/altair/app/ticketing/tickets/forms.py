# -*- coding: utf-8 -*-

import json
import os.path
#import xml.etree.ElementTree as etree
from wtforms import Form
from wtforms import TextField, IntegerField, HiddenField, SelectMultipleField, FileField
from wtforms.validators import Regexp, Length, Optional, ValidationError, StopValidation
from wtforms.widgets import TextArea
from sqlalchemy.orm.exc import NoResultFound
from altair.formhelpers import DateTimeField, Translations, Required
from altair.formhelpers.form import OurForm
from altair.formhelpers.fields import OurSelectField, OurBooleanField
from altair.formhelpers.widgets.select import BooleanSelect
from altair.app.ticketing.core.models import (
    DeliveryMethod,
    TicketFormat,
    Ticket
)
from altair.svg.geometry import as_user_unit
from altair.app.ticketing.tickets.constants import PAPERS, ORIENTATIONS
from altair.app.ticketing.tickets.cleaner.api import get_validated_svg_cleaner
from altair.app.ticketing.payments.plugins import SEJ_DELIVERY_PLUGIN_ID

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

class TicketCoverForm(OurForm):
    def _get_translations(self):
        return Translations()

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        super(TicketCoverForm, self).__init__(formdata=formdata, obj=obj, prefix=prefix, **kwargs)
        if 'organization_id' in kwargs:
            self.ticket.choices = [
                (ticket.id, ticket.name) for ticket in Ticket.query.filter_by(organization_id=kwargs['organization_id'], event_id=None)
            ]

    name = TextField(
        label = u'名前',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )

    ticket = OurSelectField(
        label=u"チケットテンプレート",
        choices=[], 
        coerce=long , 
        validators=[Required()]
    )

class TicketTemplateForm(OurForm):
    def _get_translations(self):
        return Translations()

    def __init__(self, formdata=None, obj=None, prefix='', context=None, **kwargs):
        super(TicketTemplateForm, self).__init__(formdata=formdata, obj=obj, prefix=prefix, **kwargs)
        self.context = context
        self.ticket_format_id.choices = [
            (format.id, format.name)
            for format in TicketFormat\
                .filter_by(organization_id=context.organization.id)\
                .filter_by(visible=True)
            ]
        if not formdata and not obj:
            self.principal.data = True

    name = TextField(
        label = u'名前',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )

    ticket_format_id = OurSelectField(
        label=u"チケット様式",
        choices=[], 
        coerce=long , 
        validators=[Required()]
    )

    drawing = FileField(
        label=u"券面データ", 
        validators=[
            FileRequired([".xml", ".svg", ".tssvg"])
        ]
     )

    always_reissueable = OurBooleanField(
        label=u"常に再発券可能"
        )

    principal = OurBooleanField(
        label=u"主券",
        widget=BooleanSelect(choices=[u'副券', u'主券'])
        )

    cover_print = OurBooleanField(
        label=u"表紙を印刷する"
        )

    def validate(self):
        if not super(type(self), self).validate():
            return False

        svgio = self.drawing.data.file
        try:
            ticket_format = TicketFormat.query.filter_by(id=self.ticket_format_id.data, organization_id=self.context.organization.id).one()
        except NoResultFound:
            errors = list(self.ticket_format_id.errors or ())
            errors.append(u'未知の券面フォーマットです')
            self.ticket_format_id.errors = errors
            return False
        try:
            cleaner = get_validated_svg_cleaner(svgio, exc_class=ValidationError,  sej=(any(delivery_method.delivery_plugin_id == SEJ_DELIVERY_PLUGIN_ID for delivery_method in ticket_format.delivery_methods)))
            self.data_value = {
                "drawing": cleaner.get_cleaned_svgio().getvalue(), 
                "vars_defaults": cleaner.vars_defaults
            }
        except ValidationError as e:
            self.drawing.errors = list(self.drawing.errors or ()) + [unicode(e)]
            self.data_value = {"drawing": None}
        return not bool(self.errors)

class TicketTemplateEditForm(OurForm):
    def _get_translations(self):
        return Translations()

    def __init__(self, formdata=None, obj=None, prefix='', context=None, **kwargs):
        super(TicketTemplateEditForm, self).__init__(formdata=formdata, obj=obj, prefix=prefix, **kwargs)
        self.context = context
        self.obj = obj
        self.ticket_format_id.choices = [
            (format.id, format.name) for format in TicketFormat.filter_by(organization_id=context.organization.id)
            ]
        self.data_value = None
        self.filename = None

    name = TextField(
        label = u'名前',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )

    ticket_format_id = OurSelectField(
        label=u"チケット様式",
        choices=[], 
        coerce=long , 
        validators=[Required()]
    )

    always_reissueable = OurBooleanField(
        label=u"常に再発券可能"
        )

    principal = OurBooleanField(
        label=u"主券",
        widget=BooleanSelect(choices=[u'副券', u'主券'])
        )

    drawing = FileField(
        label=u"券面データ", 
        validators=[
            FileRequired([".xml", ".svg", ".tssvg"]).none_is_ok
        ]
    )

    cover_print = OurBooleanField(
        label=u"表紙を印刷する"
        )

    def validate(self):
        if not super(type(self), self).validate():
            return False

        validate_only = False
        filename = None

        if filestorage_has_file(self.drawing.data):
            svgio = self.drawing.data.file
            filename = self.drawing.data.filename
        else:
            from cStringIO import StringIO
            svgio = StringIO(self.obj.data["drawing"].encode("utf-8"))
            validate_only = True
        self.filename = filename

        try:
            ticket_format = TicketFormat.query.filter_by(id=self.ticket_format_id.data, organization_id=self.context.organization.id).one()
        except NoResultFound:
            self.ticket_format_id.errors = list(self.ticket_format_id.errors or ()) + u'未知の券面フォーマットです'
            return False
        try:
            cleaner = get_validated_svg_cleaner(svgio, exc_class=ValidationError,  sej=(any(delivery_method.delivery_plugin_id == SEJ_DELIVERY_PLUGIN_ID for delivery_method in ticket_format.delivery_methods)))
            self.data_value = {
                "drawing": cleaner.get_cleaned_svgio().getvalue(), 
                "vars_defaults": cleaner.vars_defaults
            }
        except ValidationError as e:
            self.drawing.errors = list(self.drawing.errors or ()) + [unicode(e)]
            if validate_only:
                self.data_value = None
            else:
                self.data_value = {"drawing": None}
        return not bool(self.errors)
        
class TicketFormatForm(OurForm):
    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        super(TicketFormatForm, self).__init__(formdata=formdata, obj=obj, prefix=prefix, **kwargs)
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
        label=u"引取方法",
        validators=[Required()], 
        coerce=long , 
        choices=[])

    display_order = IntegerField(
        label=u'表示順',
        validators=[Optional()],
        default=1
    )

    visible = OurBooleanField(
        label=u'チケット様式を使用する',
        default=True,
    )

    def validate_display_order(form, field):
        if -2147483648 > field.data or field.data > 2147483647:
            raise ValidationError(u'-2147483648から、2147483647の間で指定できます。')

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
    display_order = IntegerField(
        label=u'表示順',
        validators=[Optional()],
        default=1
    )

    def validate_display_order(form, field):
        if -2147483648 > field.data or field.data > 2147483647:
            raise ValidationError(u'-2147483648から、2147483647の間で指定できます。')

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
