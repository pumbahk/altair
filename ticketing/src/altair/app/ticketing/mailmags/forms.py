# encoding: utf-8

from wtforms import HiddenField
from wtforms.validators import Regexp, Length, Optional, ValidationError
from wtforms.widgets import TextArea, CheckboxInput
from altair.formhelpers import OurForm, OurBooleanField, OurTextField, OurDateTimeField, Translations, Required
from altair.app.ticketing.core.models import Event, Account

class MailMagazineForm(OurForm):
    def _get_translations(self):
        return Translations()

    id = HiddenField(
        label=u'ID',
        validators=[Optional()],
    )
    name = OurTextField(
        label=u'メールマガジン名称',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
            ]
        )
    description = OurTextField(
        label=u'メールマガジン説明文',
        widget=TextArea(),
        validators=[
            Required(),
            Length(max=1024)
            ]
        )

    status = OurBooleanField(
        label=u'メールマガジンの有効/無効',
        default=True,
        widget=CheckboxInput()
    )
