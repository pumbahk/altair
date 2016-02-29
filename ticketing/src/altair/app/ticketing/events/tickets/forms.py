# -*- coding: utf-8 -*-

import json
import os.path
from wtforms import Form
from wtforms import TextField, IntegerField, HiddenField, SelectField, SelectMultipleField, FileField, RadioField
from wtforms.validators import Regexp, Length, Optional, ValidationError, StopValidation
from wtforms.widgets import TextArea
from altair.formhelpers import DateTimeField, Translations, Required
from altair.formhelpers.fields import BugFreeSelectField as SelectField
from altair.app.ticketing.core.models import Ticket, Product, ProductItem, TicketBundleAttribute
from altair.formhelpers.form import OurForm
from altair.formhelpers.fields import OurBooleanField, OurTextField
from altair.app.ticketing.core.models import (
    TicketFormat,
)
from StringIO import StringIO

class BoundTicketForm(Form):
    def _get_translations(self):
        return Translations()

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata=formdata, obj=obj, prefix=prefix, **kwargs)
        if 'organization_id' in kwargs:
            self.ticket_template.choices = [
                (ticket.id, ticket.name)\
                for ticket in Ticket.templates_query()\
                    .filter_by(organization_id=kwargs['organization_id'])\
                    .filter_by(visible=True)
            ]

    ticket_template = SelectField(
        label=u"チケットテンプレート",
        choices=[],
        coerce=long
        )

    name = TextField(
        label=u"券面名称",
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください')
            ]
        )

class AttributeForm(Form):
    def _get_translations(self):
        return Translations()

    def __init__(self, formdata=None, obj=None, prefix="", **kwargs):
        Form.__init__(self, formdata=formdata, obj=obj, prefix=prefix, **kwargs)
        self.bundle_id = kwargs["bundle_id"] if 'bundle_id' in kwargs else None
        self.attribute_id = kwargs["attribute_id"] if 'attribute_id' in kwargs else None

    def validate_name(form, field):
        qs = TicketBundleAttribute.filter(TicketBundleAttribute.name==field.data)\
            .filter(TicketBundleAttribute.ticket_bundle_id==form.bundle_id)
        if form.attribute_id:
            qs = qs.filter(TicketBundleAttribute.id!=form.attribute_id)
        if qs.count() >= 1:
            raise ValidationError(u"既にその名前(%s)で属性(TicketBundleAttribute)が登録されています" % field.data)

    name = TextField(
        label = u'名前(key)',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )

    value = TextField(
        label = u"データ(value)", 
        validators=[
            ], 
        widget=TextArea()
        )

class AttributesForm(Form):
    def __init__(self, formdata=None, obj=None, prefix="", **kwargs):
        if 'attrs' in kwargs:
            for a in kwargs['attrs']:
                kwargs['attr_%u' % a.id] = a.value;
        Form.__init__(self, formdata=formdata, obj=obj, prefix=prefix, **kwargs)

    @classmethod
    def append_fields(cls, attrs):
        for attr in attrs:
            cls = cls.append_field(attr)
        return cls

    @classmethod
    def append_field(cls, attr):
        setattr(cls, 'attr_%u' % attr.id, TextField(
            label = attr.name,
            validators=[
                    ], 
            widget=TextArea()
            )
        )
        return cls

class BundleForm(Form):
    def _get_translations(self):
        return Translations()

    def __init__(self, formdata=None, obj=None, prefix="", **kwargs):
        Form.__init__(self, formdata=formdata, obj=obj, prefix=prefix, **kwargs)
        if 'event_id' in kwargs:
            self.tickets.choices = [
                (ticket.id, ticket.name) for ticket in Ticket.filter_by(event_id=kwargs['event_id'])
            ]
            ## これの必要性がわからない
            ## qs = ProductItem.query.filter_by(deleted_at=None).join(Product).filter(Product.event_id==kwargs["event_id"])

    name = TextField(
        label=u"名称", 
        validators=[Required()]
        )

    tickets = SelectMultipleField(
        label=u"チケット券面",
        validators=[Required()], 
        coerce=long , 
        choices=[])


class EasyCreateKindsChoiceForm(OurForm):
    def configure(self, event):
        self.event_id.choices = [
            ("", u"基本券面から"), 
            (unicode(event.id), u"既存の券面から")
        ]
        return self

    @property
    def ticket_kind(self):
        return self.event_id

    event_id= RadioField(
        label=u"作成方法",
        validators=[Optional()],
        coerce=unicode,
        choices=[]
    )

    preview_type = RadioField(
        label=u"利用目的",
        validators=[Required()],
        coerce=unicode,
        choices=[("default", u"自社発券"), ("sej", u"SEJ発券")]
    )
    

class EasyCreateTemplateChoiceForm(OurForm):
    def configure(self, ticket_templates):
        self.templates.choices = [(unicode(t.id),t.name) for t in ticket_templates]
        return self

    templates = SelectField(
        label=u"チケットテンプレート",
        validators=[Required()], 
        coerce=unicode, 
        choices=[])

from altair.app.ticketing.tickets.cleaner.api import get_validated_svg_cleaner

class EasyCreateTranscribeForm(OurForm):
    def _get_translations(self):
        return Translations()

    name = TextField(
        label = u'名前',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )

    base_template_id = SelectField(
        label=u"template側",
        choices=[],
        coerce=long,
        validators=[Required()]
    )

    mapping_id = SelectField(
        label=u"mapping側",
        choices=[],
        coerce=long,
        validators=[Required()]
    )

    def configure(self, base_template_choices, mapping_choices):
        self.base_template_id.choices = base_template_choices
        self.mapping_id.choices = mapping_choices
        return self

class EasyCreateTemplateUploadForm(OurForm):
    def _get_translations(self):
        return Translations()

    name = TextField(
        label = u'名前',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )

    preview_type = RadioField(
        label=u"利用目的",
        validators=[Optional()],
        coerce=unicode,
        default="default",
        choices=[("default", u"自社発券"), ("sej", u"SEJ発券")]
    )

    ticket_format_id = SelectField(
        label=u"チケット様式",
        choices=[],
        coerce=long,
        validators=[Required()]
    )

    always_reissueable = OurBooleanField(
        label=u"常に再発券可能"
        )

    principal = OurBooleanField(
        label=u"手数料計算に含める"
        )

    cover_print = OurBooleanField(
        label=u"表紙を印刷する"
        )

    drawing = HiddenField()
    fill_mapping = HiddenField()
    event_id = HiddenField()

    def configure(self, event, ticket=None):
        if ticket:
            self.ticket_format_id.choices = [(long(f.id), f.name) for f in [ticket.ticket_format]]
            self.ticket_format_id.data = long(ticket.ticket_format.id)
        self.event_id.data = event.id
        return self

    def validate(self):
        if not super(type(self), self).validate():
            return False

        svgio = StringIO(self.drawing.data)
        try:
            cleaner = get_validated_svg_cleaner(svgio, exc_class=ValidationError,  sej=self.data["preview_type"] == "sej")
            self.data_value = {
                "drawing": cleaner.get_cleaned_svgio().getvalue(), 
                "fill_mapping": json.loads(self.fill_mapping.data), 
                "vars_defaults": cleaner.vars_defaults
            }
        except ValueError as e:
            self.name.errors = list(self.drawing.errors or ()) + [unicode(e)]
            self.data_value = {"drawing": None}
        except ValidationError as e:
            self.name.errors = list(self.drawing.errors or ()) + [unicode(e)]
            self.data_value = {"drawing": None}
        return not bool(self.errors)
