# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, SelectField, HiddenField
from wtforms.validators import Regexp, Length, Optional, ValidationError

from ticketing.formhelpers import DateTimeField, Translations, Required
from ticketing.core.models import Venue, Account, Performance

class PerformanceForm(Form):
    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata, obj, prefix, **kwargs)
        if 'organization_id' in kwargs:
            conditions = {'organization_id':kwargs['organization_id']}
            if 'venue_id' in kwargs:
                conditions.update({'id':kwargs['venue_id']})
            else:
                conditions.update({'original_venue_id':None})
            self.venue_id.choices = [
                (venue.id, venue.name) for venue in Venue.filter_by(**conditions).all()
            ]

    def _get_translations(self):
        return Translations()

    id = HiddenField(
        label=u'ID',
        validators=[Optional()],
    )
    name = TextField(
        label=u'公演名',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ],
    )
    code = TextField(
        label=u'公演コード',
        validators=[
            Required(),
            Regexp(u'^[a-zA-Z0-9]*$', message=u'英数字のみ入力できます'),
            Length(min=12, max=12, message=u'12文字で入力してください'),
        ],
    )
    open_on = DateTimeField(
        label=u'開場',
        validators=[Optional()],
        format='%Y-%m-%d %H:%M',
    )
    start_on = DateTimeField(
        label=u'開演',
        validators=[Required()],
        format='%Y-%m-%d %H:%M',
    )
    end_on = DateTimeField(
        label=u'終演',
        validators=[Optional()],
        format='%Y-%m-%d %H:%M',
    )
    venue_id = SelectField(
        label=u'会場',
        validators=[Required(u'選択してください')],
        choices=[],
        coerce=int,
    )
    original_id = HiddenField(
        validators=[Optional()],
    )

    def validate_start_on(form, field):
        if field.data and form.open_on.data and field.data < form.open_on.data:
            raise ValidationError(u'開場日時より過去の日時は入力できません')

    def validate_end_on(form, field):
        if field.data and form.start_on.data and field.data < form.start_on.data:
            raise ValidationError(u'開演日時より過去の日時は入力できません')

    def validate_code(form, field):
        if form.id and form.id.data:
            return
        if field.data and Performance.filter_by(code=field.data).count():
            raise ValidationError(u'既に使用されています')
