# coding: utf-8
from altaircms.formhelpers import Form
from wtforms import fields, widgets, validators
from wtforms.ext.sqlalchemy import fields as sa_fields

from altaircms.models import DBSession
from .models import PERMISSIONS, OperatorSelfAuth

class SelfLoginForm(Form):
    organization_id = fields.SelectField(
        label=u"所属",
        choices = [],
        coerce=unicode,
        validators=[validators.Required()]
    )
    name = fields.TextField(
        label=u"ユーザ名",
        validators=[validators.Required()]
    )
    password = fields.TextField(
        label=u"パスワード",
        validators=[validators.Required()]
    )

    def configure(self, orgs):
        self.organization_id.choices = [(o.id, o.name) for o in orgs]
        return self

    def validate(self):
        super(SelfLoginForm, self).validate()
        if "organization_id" in self.errors:
            del self.errors["organization_id"] # xxx:

        if bool(self.errors):
            return False

        self.user = OperatorSelfAuth.get_login_user(
            self.data["organization_id"],
            self.data["name"],
            self.data["password"]
            )
        if self.user is None:
            self.errors["name"] = [u"ユーザかパスワードが間違っています"]
            return False
        return True

class APIKeyForm(Form):
    name = fields.TextField(
        validators=[validators.Required()]
    )

class RoleForm(Form):
    permission = fields.SelectField(
        choices=[(p, p) for p in PERMISSIONS],
    )

class NowSettingForm(Form):
    now = fields.DateTimeField(label=u"時間指定現在時刻")

    __display_fields__ = ["now"]

class OrganizationForm(Form):
    name = fields.TextField(
        label=u"組織名",
        validators=[validators.Required()]
    )
    backend_id = fields.IntegerField(
        label=u"backend_id",
    )
    short_name = fields.TextField(
        label=u"略称",
        validators=[validators.Required()]
    )
    code = fields.TextField(
        label=u"組織コード(2桁英字大文字)",
        validators=[validators.Required()]
    )
    prefecture = fields.TextField(
        label=u"都道府県",
    )
    address = fields.TextField(
        label=u"住所(都道府県以下)",
    )
    email = fields.TextField(
        label=u"メールアドレス",
    )
    auth_source = fields.TextField(
        label=u"auth_source",
        default=u"oauth",
    )
    use_full_usersite = fields.BooleanField(
        label=u"PC以外のview有効化",
        default=False
    )
    use_only_one_static_page_type = fields.BooleanField(
        label=u"smartphoneでのPCページ閲覧",
        default=True
    )

    __display_fields__ = ["name", "backend_id", "short_name", "code", "prefecture", "address", "email", "auth_source", "use_full_usersite", "use_only_one_static_page_type"]

class HostForm(Form):
    organization_id = fields.SelectField(
        label=u'organization_id',
        choices=[],
        coerce=unicode,
    )
    host_name = fields.TextField(
        label=u"host_name",
        validators=[validators.Required()],
    )
    cart_domain = fields.TextField(
        label=u"cart_domain",
        default=u"https://",
        validators=[validators.Required()],
    )

    __display_fields__ = ["organization_id", "host_name", "cart_domain"]

    def configure(self, orgs):
        self.organization_id.choices = [(o.id, o.name) for o in orgs]
        self.organization_id.choices.reverse()
        return self

    def validate(self):
        super(HostForm, self).validate()
        if "organization_id" in self.errors:
            del self.errors["organization_id"] # xxx:

        return True
