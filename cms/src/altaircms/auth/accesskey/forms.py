# -*- coding:utf-8 -*-

import logging 
logger = logging.getLogger(__name__)
from altaircms.formhelpers import Form
from wtforms import fields
from wtforms import widgets
from wtforms import validators
from altaircms.auth.models import PageAccesskey

class AccessKeyForm(Form):
    name = fields.TextField(label=u"名前")
    expiredate = fields.DateTimeField(label=u"有効期限", validators=[validators.Optional()])
    scope = fields.SelectField(label=u"scope", choices=[(x, x) for x in PageAccesskey.SCOPE_CANDIDATES])

    display_fields =["name", "expiredate", "scope"]
