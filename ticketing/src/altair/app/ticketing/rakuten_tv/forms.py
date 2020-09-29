# -*- coding: utf-8 -*-
from altair.formhelpers.fields import OurTextField, OurTextAreaField, DateTimeField
from altair.formhelpers.form import OurForm
from altair.formhelpers import after1900
from wtforms.validators import Optional
from wtforms.fields import (
     HiddenField,
     BooleanField,
)


class RakutenTvSettingForm(OurForm):

    id = HiddenField(
        label=u'ID',
        validators=[Optional()],
    )
    available_flg = BooleanField(
        label=u'使用可否',
        validators=[Optional()],
    )
    rtv_endpoint_url = OurTextField(
        label=u"EndPoint",
        note=u"EndPoint",
    )
    release_date = DateTimeField(
        label=u"URL公開日時",
        validators=[Optional(), after1900],
        format='%Y-%m-%d %H:%M',
    )
    description = OurTextAreaField(
        label=u"説明文",
        note=u"説明文",
    )
