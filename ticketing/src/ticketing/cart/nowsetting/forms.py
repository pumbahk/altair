# -*- coding:utf-8 -*-
from altair.formhelpers import DateTimeField, Translations, Required
from wtforms import Form

class NowSettingForm(Form):
    def _get_translations(self):
        return Translations()
    now = DateTimeField(label=u"現在時刻", validators=[Required()])

