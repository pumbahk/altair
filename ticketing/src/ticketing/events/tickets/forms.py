# -*- coding: utf-8 -*-

import json
import os.path
from wtforms import Form
from wtforms import TextField, IntegerField, HiddenField, SelectField, SelectMultipleField, FileField
from wtforms.validators import Regexp, Length, Optional, ValidationError, StopValidation
from wtforms.widgets import TextArea
from ticketing.formhelpers import DateTimeField, Translations, Required
from ticketing.core.models import Ticket, Product, ProductItem, TicketBundleAttribute

class BoundTicketForm(Form):
    def _get_translations(self):
        return Translations()

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata=formdata, obj=obj, prefix=prefix, **kwargs)
        if 'organization_id' in kwargs:
            self.ticket_template.choices = [
                (ticket.id, ticket.name) for ticket in Ticket.templates_query().filter_by(organization_id=kwargs['organization_id'])
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
        if 'bundle_id' in kwargs:
            self.bundle_id = kwargs["bundle_id"]
        else:
            self.bundle_id = None

    def validate_name(form, field):
        qs = TicketBundleAttribute.filter(TicketBundleAttribute.name==field.data)
        qs = qs.filter(TicketBundleAttribute.ticket_bundle_id==form.bundle_id)
        if qs.with_entities("id").first():
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
            Required(), 
            ## json?
            ], 
        widget=TextArea()
        )

class AttributeEditForm(Form):
    def _get_translations(self):
        return Translations()

    def __init__(self, formdata=None, obj=None, prefix="", **kwargs):
        Form.__init__(self, formdata=formdata, obj=obj, prefix=prefix, **kwargs)
        self.bundle_id = kwargs["bundle_id"] if 'bundle_id' in kwargs else None
        self.attribute_id = kwargs["attribute_id"] if 'attribute_id' in kwargs else None

    def validate_name(form, field):
        qs = TicketBundleAttribute.filter(TicketBundleAttribute.name==field.data)\
            .filter(TicketBundleAttribute.ticket_bundle_id==form.bundle_id)\
            .filter(TicketBundleAttribute.id!=form.attribute_id)
        
        if qs.with_entities("id").first():
            raise ValidationError(u"自分以外で既にその名前(%s)で属性(TicketBundleAttribute)が登録されています" % field.data)

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
            Required(), 
            ## json?
            ], 
        widget=TextArea()
        )

class BundleForm(Form):
    def _get_translations(self):
        return Translations()

    def __init__(self, formdata=None, obj=None, prefix="", **kwargs):
        Form.__init__(self, formdata=formdata, obj=obj, prefix=prefix, **kwargs)
        if 'event_id' in kwargs:
            self.tickets.choices = [
                (ticket.id, ticket.name) for ticket in Ticket.filter_by(event_id=kwargs['event_id'])
            ]
            qs = ProductItem.query.filter_by(deleted_at=None).join(Product).filter(Product.event_id==kwargs["event_id"])
            self.product_items.choices = [
                (item.id, item.name) for item in qs
            ]

    name = TextField(
        label=u"名称", 
        validators=[Required()]
        )

    tickets = SelectMultipleField(
        label=u"チケット券面",
        validators=[Required()], 
        coerce=long , 
        choices=[])

    product_items = SelectMultipleField(
        label=u"商品(ProductItem)",
        validators=[Required()], 
        coerce=long , 
        choices=[])
