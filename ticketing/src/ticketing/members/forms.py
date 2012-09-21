# -*- coding:utf-8 -*-
import json
import itertools
from wtforms import Form
from wtforms import fields
from wtforms import widgets
from wtforms import validators
from collections import namedtuple, OrderedDict

class MemberShipChoicesForm(Form):
    membership_id = fields.SelectField(
        label=u"Membership", 
        choices=[], 
        coerce=unicode
        )
    
    def configure(self, memberships):
        self.membership_id.choices = [(m.id, m.name) for m in memberships]
        return self

class MemberGroupChoicesForm(Form):
    membergroup_id = fields.SelectField(
        label=u"Membergroup", 
        choices=[], 
        coerce=unicode
        )

    user_id_list = fields.HiddenField(
        label=u"", 
        )
    def validate_user_id_list(form, field):
        field.data = json.loads(field.data)

    def configure(self, membergroups):
        self.membergroup_id.choices = [(m.id, m.name) for m in membergroups]
        return self

    def validate(self):
        super(self.__class__, self).validate()
        if "membergroup_id" in self.errors:
            del self.errors["membergroup_id"] #xxx:
        return not bool(self.errors)

