# -*- coding: utf-8 -*-
from altair.formhelpers.fields import OurTextField, OurTextAreaField
from altair.formhelpers.form import OurForm
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
    description = OurTextAreaField(
        label=u"説明文",
        note=u"説明文",
    )
