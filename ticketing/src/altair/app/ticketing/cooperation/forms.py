#-*- coding: utf-8 -*-
from wtforms import Form, HiddenField, SelectField, FileField
from wtforms.validators import Optional
from altair.formhelpers import Required, Translations
from altair.app.ticketing.core.models import CooperationTypeEnum

class CooperationUpdateForm(Form):
    def _get_translations(self):
        return Translations()

    id = HiddenField(
        label=u'ID',
        validators=[Optional()],
    )

    cooperation_type = SelectField(
        label=u'連携タイプ',
        validators=[Required(u'選択してください')],
        choices=[coop_type.v for coop_type in CooperationTypeEnum],
        coerce=int,
    )
    
    cooperation_file = FileField(
        u'CSVファイル',
        validators=[],
    )


class CooperationDownloadForm(Form):
    id = HiddenField(
        label=u'ID',
        validators=[Optional()],
    )


    cooperation_type = SelectField(
        label=u'連携タイプ',
        validators=[Required(u'選択してください')],
        choices=[coop_type.v for coop_type in CooperationTypeEnum],
        coerce=int,
    )
