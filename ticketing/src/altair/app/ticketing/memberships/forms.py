# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, HiddenField, DateField, PasswordField, SelectField, BooleanField, SelectMultipleField
from wtforms.validators import Length, Optional
from altair.formhelpers import DateTimeField, Translations, Required
from altair.app.ticketing.core import models as cmodels


class MembershipForm(Form):
    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata, obj, prefix, **kwargs)
        if obj:
            self.name.data = obj.name
            self.membership_id.data = obj.id
            self.organization_id.data = obj.organization_id
        # self.organization_id.choices = [(unicode(o.id), o.name) for o in cmodels.Organization.query]

    def _get_translations(self):
        return Translations()
    # organization_id = SelectField(
    #     label=u"取引先名", 
    #     choices=[], 
    #     coerce=unicode, 
    #     validators=[Optional()],
    # )
    organization_id = HiddenField(
        label=u"取引先名", 
        validators=[Optional()],
    )
    
    name = TextField(
        label=u'名前',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ])
    display_name = TextField(
        label=u'表示名',
        validators=[
            Optional(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ])
    memo = TextField(
        label=u'種別情報',
        validators=[
            Optional(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ])
    membership_id = HiddenField(
        label=u'ID',
        validators=[Optional()],
    )
    enable_auto_input_form = BooleanField(
        label=u"自動フォーム入力",
        default=True
        )
    enable_point_input = BooleanField(
        label=u"楽天ポイント手入力",
        default=True
        )

class MemberGroupDeleteForm(Form):
    def _get_translations(self):
        return Translations()

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata, obj, prefix, **kwargs)
        if obj:
            self.membership_id.data = obj.membership_id
            self.membergroup = obj

    def validate(self):
        status = super(MemberGroupDeleteForm, self).validate()
        if not status:
            return status
        if not hasattr(self, "membergroup"):
            return status
        membergroup = self.membergroup
        if len(membergroup.users) > 0:
            self.membership_id.errors = [u"{membergroup.name}には１つ以上の会員が存在しています。消せません。".format(membergroup=membergroup)]
        if len(membergroup.sales_segment_groups) > 0:
            self.membership_id.errors = [u"{membergroup.name}には１つ以上の販売区分グループが紐ついています。消せません。".format(membergroup=membergroup)]
        return not bool(self.errors)

    membership_id = HiddenField(
        label=u"",
    )
    redirect_to = HiddenField(
        label=u"",
        validators=[Optional()]
    )


class MemberGroupForm(Form):
    def _get_translations(self):
        return Translations()

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata, obj, prefix, **kwargs)
        if obj:
            self.id.data = obj.id
            self.name.data = obj.name
            self.is_guest.data = obj.is_guest
            self.membership_id.data = obj.membership_id

    id = HiddenField(
        label=u'ID',
        validators=[Optional()],
    )

    name = TextField(
        label=u"名前"
        )

    is_guest = BooleanField(
        label=u"ゲストログイン"
        )

    membership_id = HiddenField(
        label=u"membership", 
        validators=[Optional()]
    )

class SalesSegmentGroupToMemberGroupForm(Form):
    def _get_translations(self):
        return Translations()

    def __init__(self, formdata=None, obj=None, prefix='', sales_segment_groups=None, events=None, **kwargs):
        Form.__init__(self, formdata, obj, prefix, **kwargs)
        sales_segment_groups = list(sales_segment_groups)
        self.sales_segment_groups.choices = [(unicode(s.id), s.name) for s in sales_segment_groups or []]
        self.event_id.choices = [(unicode(s.id), s.title) for s in events or []]
        self.sales_segment_groups_height = "%spx" % (len(sales_segment_groups)*20)
        if obj:
            self.sales_segment_groups.data = [unicode(s.id) for s in obj.sales_segments]

    sales_segment_groups = SelectMultipleField(
        label=u"販売区分グループ",
        choices=[], 
        coerce=unicode, 
    )

    event_id = SelectField(
        label=u"イベント", 
        choices=[], 
        coerce=unicode, 
        )
