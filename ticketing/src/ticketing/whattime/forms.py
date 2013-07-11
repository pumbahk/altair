# -*- coding:utf-8 -*-
from altair.formhelpers import DateTimeField, Translations, Required
from wtforms import Form
from wtforms import validators
from wtforms.fields import TextField
class NowSettingForm(Form):
    def _get_translations(self):
        return Translations()
    now = DateTimeField(label=u"現在時刻", validators=[Required()])
    redirect_to = TextField(label=u"リダイレクト先", validators=[validators.Optional(), validators.URL])
    

