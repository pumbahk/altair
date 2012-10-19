# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, HiddenField, DateField, PasswordField, SelectField, BooleanField, SelectMultipleField
from wtforms.validators import Length, Email, Optional
from ticketing.formhelpers import DateTimeField, Translations, Required
from ticketing.core import models as cmodels


class MembershipForm(Form):

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata, obj, prefix, **kwargs)
        if obj:
            self.name.data = obj.name
            self.membership_id.data = obj.id
            self.organization_id.data = obj.organization_id
        # self.organization_id.choices = [(unicode(o.id), o.name) for o in cmodels.Organization.query]

    def _get_translations(self):
        return Translations()
    # organization_id = SelectField(
    #     label=u"取引先名", 
    #     choices=[], 
    #     coerce=unicode, 
    #     validators=[Optional()],
    # )
    organization_id = HiddenField(
        label=u"取引先名", 
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

class SalesSegmentToMemberGroupForm(Form):
    def _get_translations(self):
        return Translations()

    def __init__(self, formdata=None, obj=None, prefix='', salessegments=None, events=None, **kwargs):
        Form.__init__(self, formdata, obj, prefix, **kwargs)
        salessegments = list(salessegments)
        self.salessegments.choices = [(unicode(s.id), s.name) for s in salessegments or []]
        self.event_id.choices = [(unicode(s.id), s.title) for s in events or []]
        self.salessegments_height = "%spx" % (len(salessegments)*20)
        if obj:
            self.salessegments.data = [unicode(s.id) for s in obj.sales_segments]

    salessegments = SelectMultipleField(
        label=u"販売区分", 
        choices=[], 
        coerce=unicode, 
    )

    event_id = SelectField(
        label=u"イベント", 
        choices=[], 
        coerce=unicode, 
        )
