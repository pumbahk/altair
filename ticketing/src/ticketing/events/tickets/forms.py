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
from ticketing.core.models import Ticket, Product, ProductItem

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


class BundleForm(Form):
    def get_translations(self):
        return Translations()

    def __init__(self, formdata=None, obj=None, prefix="", **kwargs):
        Form.__init__(self, formdata=formdata, obj=obj, prefix=prefix, **kwargs)
        if 'event_id' in kwargs:
            self.tickets.choices = [
                (ticket.id, ticket.name) for ticket in Ticket.filter_by(event_id=kwargs['event_id'])
            ]
            self.product_items.choices = [
                (item.id, item.name) for item in ProductItem.query.filter_by(deleted_at=None)
            ]

    name = TextField(
        label=u"名称", 
        validators=[Required()]
        )

    tickets = SelectMultipleField(
        label=u"チケットテンプレート",
        validators=[Required()], 
        coerce=long , 
        choices=[])

    product_items = SelectMultipleField(
        label=u"商品(ProductItem)",
        validators=[Required()], 
        coerce=long , 
        choices=[])
