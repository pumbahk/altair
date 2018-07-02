# -*- coding: utf-8 -*-

from altair.formhelpers import Required, OurBooleanField
from altair.formhelpers.fields import OurTextField, OurSelectField, OurHiddenField, OurDateField
from altair.formhelpers.form import OurForm
from altair.formhelpers.validators import after1900
from altair.saannotation import get_annotations_for
from wtforms.validators import Length, Optional

from ..models import Passport, PassportNotAvailableTerm


class PassportForm(OurForm):
    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        OurForm.__init__(self, formdata, obj, prefix, **kwargs)
        self.exist_passport_performance = None
        if "organization_id" in kwargs:
            self.organization_id.data = kwargs['organization_id']
        if "exist_passport_performance" in kwargs:
            self.exist_passport_performance = kwargs['exist_passport_performance']

    id = OurHiddenField(
        label=get_annotations_for(Passport.id)['label'],
        validators=[Optional()]
    )
    organization_id = OurHiddenField(
        label=get_annotations_for(Passport.organization_id)['label'],
        validators=[Optional()]
    )
    performance_id = OurSelectField(
        label=get_annotations_for(Passport.performance_id)['label'],
        validators=[Required(u'選択してください')],
        choices=[],
        coerce=int
    )
    name = OurTextField(
        label=get_annotations_for(Passport.name)['label'],
        validators=[
            Required(),
            Length(max=1024, message=u'1024文字以内で入力してください'),
        ]
    )
    available_day = OurTextField(
        label=get_annotations_for(Passport.available_day)['label'],
        validators=[
            Required(),
            Length(max=255, message=u'255桁以内で入力してください'),
        ]
    )
    daily_passport = OurBooleanField(
        label=get_annotations_for(Passport.daily_passport)['label']
    )
    is_valid = OurBooleanField(
        label=get_annotations_for(Passport.is_valid)['label'],
        default=True
    )

    def set_performance_choices(self, performances):
        self.performance_id.choices = [(performance.id, u"{0} {1}".format(performance.event.title, performance.name))
                                       for
                                       performance in performances]

    def validate(self, pdp=None):
        # このように and 演算子を展開しないとすべてが一度に評価されない
        status = super(PassportForm, self).validate()
        status = all([status, self._validate_performance_id(), self._validate_available_day()])
        return status

    def _validate_performance_id(self, *args, **kwargs):
        if self.exist_passport_performance:
            self.performance_id.errors.append(u"パスポート設定は１つのパフォーマンスにのみ紐付けられます")
            return False
        return True

    def _validate_available_day(self, *args, **kwargs):
        if not self.available_day.data.isdigit():
            self.available_day.errors.append(u"数字で入力してください")
            return False
        if int(self.available_day.data) < 1:
            self.available_day.errors.append(u"１日以上で入力してください")
            return False
        self.available_day.data = int(self.available_day.data)
        return True


class PassportNotAvailableTermForm(OurForm):
    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        OurForm.__init__(self, formdata, obj, prefix, **kwargs)

    id = OurHiddenField(
        label=get_annotations_for(PassportNotAvailableTerm.id)['label'],
        validators=[Optional()]
    )
    start_on = OurDateField(
        label=u'入場不可時間',
        validators=[Optional(), after1900],
        format='%Y-%m-%d %H:%M',
    )
    end_on = OurDateField(
        label=u'入場不可終了時間',
        validators=[Optional(), after1900],
        format='%Y-%m-%d %H:%M',
    )
