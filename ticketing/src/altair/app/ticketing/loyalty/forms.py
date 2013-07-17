# encoding: utf-8

from wtforms.fields import HiddenField
from wtforms.validators import Optional
from altair.app.ticketing.helpers import label_text_for
from altair.formhelpers import Translations
from altair.formhelpers.form import OurForm
from altair.formhelpers.validators import Required
from altair.formhelpers.fields import OurTextField, OurDecimalField, OurDateTimeField, PercentageField, OurSelectField, OurGroupedSelectMultipleField
from altair.app.ticketing.users import models as user_models
from wtforms.validators import ValidationError
from .models import PointGrantSetting
from ..models import HyphenationCodecMixin
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import asc, and_
from ..core.models import Event, Product, SalesSegmentGroup, SalesSegment
from . import helpers as lh

class PointGrantSettingForm(OurForm):
    def _get_translations(self):
        return Translations()

    id = HiddenField(
        label=label_text_for(PointGrantSetting.id),
        validators=[Optional()]
        )

    name = OurTextField(
        label=label_text_for(PointGrantSetting.name),
        validators=[Required()]
        )

    type = OurSelectField(
        label=label_text_for(PointGrantSetting.type),
        choices=[(v.v, lh.format_point_type(v.v)) for v in user_models.UserPointAccountTypeEnum._values],
        coerce=long
        )

    fixed = OurDecimalField(
        label=label_text_for(PointGrantSetting.fixed),
        validators=[Optional()]
        )

    rate = PercentageField(
        label=label_text_for(PointGrantSetting.rate),
        validators=[Optional()],
        precision=0
        )

    start_at = OurDateTimeField(
        label=label_text_for(PointGrantSetting.start_at),
        validators=[Optional()]
        )

    end_at = OurDateTimeField(
        label=label_text_for(PointGrantSetting.end_at),
        validators=[Optional()]
        )

    def validate_name(self, field):
        if PointGrantSetting.query.filter(and_(PointGrantSetting.name == field.data, PointGrantSetting.organization_id == self.context.user.organization_id, PointGrantSetting.id != (self.context.point_grant_setting and self.context.point_grant_setting.id or None))).first() is not None:
            raise ValidationError(u'同じ名前の設定が既に存在します')

    def validate(self, *args, **kwargs):
        if not super(self.__class__, self).validate(*args, **kwargs):
            return False
        if not self.rate.data and not self.fixed.data:
            self.rate.errors.append(u'%sと%sの両方が空です' % (self.fixed.label.text, self.rate.label.text))
            return False
        return True

    def __init__(self, *args, **kwargs):
        self.context = kwargs.pop('context', None)
        super(PointGrantSettingForm, self).__init__(*args, **kwargs)
