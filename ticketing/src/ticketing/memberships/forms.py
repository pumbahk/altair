# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, HiddenField, DateField, PasswordField, SelectField, BooleanField
from wtforms.validators import Length, Email, Optional
from ticketing.formhelpers import DateTimeField, Translations, Required
from ticketing.core import models as cmodels


class MembershipForm(Form):

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata, obj, prefix, **kwargs)
        if obj:
            self.name.data = obj.name
            self.membership_id.data = obj.id
        self.organization_id.choices = [(unicode(o.id), o.name) for o in cmodels.Organization.query]

    def _get_translations(self):
        return Translations()
    organization_id = SelectField(
        label=u"会社名", 
        choices=[], 
        coerce=unicode, 
        validators=[Optional()],
    )
    name = TextField(
        label=u'名前',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ])
    membership_id = HiddenField(
        label=u'ID',
        validators=[Optional()],
    )

class MemberGroupForm(Form):
    def _get_translations(self):
        return Translations()

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata, obj, prefix, **kwargs)
        if obj:
            self.id.data = obj.id
            self.name.data = obj.name
            self.is_guest.data = obj.is_guest
            self.membership_id.data = obj.membership_id

    id = HiddenField(
        label=u'ID',
        validators=[Optional()],
    )

    name = TextField(
        label=u"名前"
        )

    is_guest = BooleanField(
        label=u"ゲストログイン"
        )

    membership_id = HiddenField(
        label=u"membership", 
        validators=[Optional()]
    )
