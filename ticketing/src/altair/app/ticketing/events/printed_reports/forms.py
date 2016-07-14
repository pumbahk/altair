# -*- coding: utf-8 -*-
from wtforms.validators import Optional, Required
from altair.formhelpers import OurForm, after1900
from altair.formhelpers.fields import OurSelectField, DateTimeField, OurTextAreaField, TimeField


class PrintedReportSettingForm(OurForm):
    start_on = DateTimeField(
        label=u'送信開始時間',
        validators=[Required(), after1900],
        format='%Y-%m-%d %H:%M',
    )
    end_on = DateTimeField(
        label=u'送信終了時間',
        validators=[Required(), after1900],
        format='%Y-%m-%d %H:%M',
    )
    time = TimeField(
        label=u'送信指定時刻',
        format='%Y-%m-%d %H:%M',
    )
    last_sent_at = DateTimeField(
        label=u'最終送信時刻',
        validators=[Optional(), after1900],
        format='%Y-%m-%d %H:%M',
    )


class PrintedReportRecipientForm(OurForm):
    recipients = OurTextAreaField(
        label=u'入力例：送信者名,test@test.com',
        validators=[Optional()],
        hide_on_new=True
    )
