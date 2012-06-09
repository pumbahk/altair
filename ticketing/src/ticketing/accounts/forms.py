# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, HiddenField, SelectField
from wtforms.validators import Length, Optional

from ticketing.formhelpers import Translations, Required
from ticketing.core.models import Organization

class AccountForm(Form):

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata, obj, prefix, **kwargs)
        self.organization_id.choices = [
            (organization.id, organization.name) for organization in Organization.all()
        ]

    def _get_translations(self):
        return Translations()

    id = HiddenField(
        label=u'ID',
        validators=[Optional()],
    )
    organization_id = SelectField(
        label=u'配券元',
        validators=[Required(u'選択してください')],
        choices=[],
        coerce=int
    )
    name = TextField(
        label=u'クライアント名',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
