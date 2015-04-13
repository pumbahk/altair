# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import HiddenField, BooleanField
from wtforms.validators import Regexp, Length, Optional, ValidationError

from altair.formhelpers import OurForm, DateTimeField, Translations, Required, RequiredOnUpdate, OurTextField, OurSelectField
from altair.app.ticketing.core.models import Account

class StockHolderForm(OurForm):
    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        super(StockHolderForm, self).__init__(formdata, obj, prefix, **kwargs)
        if 'organization_id' in kwargs:
            self.account_id.choices = [
                (account.id, account.name) for account in Account.filter_by_organization_id(kwargs['organization_id'])
            ]
        self.organization_id = kwargs['organization_id'] or None

    def _get_translations(self):
        return Translations()

    id = HiddenField(
        validators=[Optional()],
    )
    event_id = HiddenField(
        validators=[Required()],
    )
    name = OurTextField(
        label=u'枠名',
        validators=[
            RequiredOnUpdate(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ],
    )
    account_id = OurSelectField(
        label=u'配券先',
        validators=[Required()],
        choices=[],
        coerce=int
    )
    text = OurTextField(
        label=u'記号',
        validators=[RequiredOnUpdate()],
    )
    text_color = OurTextField(
        label=u'記号色',
        validators=[RequiredOnUpdate()],
    )
    is_putback_target = BooleanField(
        label=u'外部返券利用',
        validators=[],
    )

    def validate_is_putback_target(self, field):
        if field.data and self.organization_id not in (15,): # rt only
            raise ValidationError(u'サポート対象外の機能です。')
