# -*- coding: utf-8 -*-

from deform.widget import SelectWidget
from colander import MappingSchema, SchemaNode, String, Int, DateTime, Bool, Decimal, Float
from ticketing.models.master import Prefecture

class OperatorRoleForm(MappingSchema):
    name = SchemaNode(String())
