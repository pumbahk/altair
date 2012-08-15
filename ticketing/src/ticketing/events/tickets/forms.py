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
from ticketing.tickets.models import Ticket

class BoundTicketForm(Form):
    def _get_translations(self):
        return Translations()

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata=formdata, obj=obj, prefix=prefix, **kwargs)
        if 'organization_id' in kwargs:
            self.ticket_template.choices = [
                (ticket.id, ticket.name) for ticket in Ticket.templates_query().filter_by(organization_id=kwargs['organization_id'])
            ]
        self._drawing = None

    ticket_template = SelectField(
        label=u"チケットテンプレート", 
        choices=[], 
        coerce=long
        )
