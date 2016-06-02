# -*- coding:utf-8 -*-
import json
import logging
from altair.app.ticketing import csvutils as csv
import itertools
from wtforms import Form
from wtforms import fields
from wtforms import widgets
from wtforms import validators
from collections import namedtuple, OrderedDict
from wtforms.validators import ValidationError
from altair.app.ticketing.users.models import Member

logger = logging.getLogger(__name__)


class SearchMemberForm(Form):
    membership_id = fields.SelectField(
        label=u"Membership",
        choices=[],
        coerce=unicode
    )
    membergroup_id = fields.SelectField(
        label=u"Membergroup",
        choices=[],
        coerce=unicode
    )
    username = fields.TextField(
        label=u"名前検索"
    )

    def configure(self, memberships, membergroups=[]):
        self.membership_id.choices = [(m.id, m.name) for m in memberships]
        self.membergroup_id.choices = [
            ("", u"-----")] + [(g.id, g.name) for g in membergroups]
        return self


class MemberCSVExportForm(Form):
    csvfile = fields.TextField(label=u"保存ファイル")
    encoding = fields.SelectField(label=u"エンコーディング",
                                  choices=(("cp932", u"windowsのファイル"), ("utf-8", u"UTF-8")))


class MemberCSVImportForm(Form):
    csvfile = fields.FileField(label=u"csvファイル名")
    encoding = fields.SelectField(label=u"エンコーディング",
                                  choices=(("cp932", u"windowsのファイル"), ("utf-8", u"UTF-8")))

    def validate(self):
        super(MemberCSVImportForm, self).validate()
        if not hasattr(self.data["csvfile"], "file"):
            self.csvfile.errors = self.errors[
                "csvfile"] = [u"csvファイルを指定してください。"]
            return not bool(self.errors)

        io = self.data["csvfile"].file
        try:
            reader = csv.reader(
                io, quotechar="'", encoding=self.data["encoding"])
            for membergroup_name, loginname, password in reader:
                pass
        except UnicodeDecodeError as e:
            logger.info("*csv import* %s" % (str(e)))
            self.csvfile.errors = self.errors["csvfile"] = [
                u"csvファイルが壊れています。あるいは指定しているエンコーディングが異なっているかもしません。"]
        except Exception as e:
            logger.info(e.__class__)
            logger.info("*csv import* %s" % (str(e)))
            self.csvfile.errors = self.errors["csvfile"] = [u"csvファイルが壊れています。"]
        io.seek(0)
        return not bool(self.errors)


class MemberGroupChoicesForm(Form):
    membergroup_id = fields.SelectField(
        label=u"Membergroup",
        choices=[],
        coerce=unicode
    )

    member_id_list = fields.HiddenField(
        label=u"",
    )

    def validate_member_id_list(form, field):
        field.data = json.loads(field.data)
        if not field.data:
            raise ValidationError("更新対象がありません")

    def configure(self, membergroups):
        self.membergroup_id.choices = [(m.id, m.name) for m in membergroups]
        return self

    def validate(self):
        super(self.__class__, self).validate()
        if "membergroup_id" in self.errors:
            del self.errors["membergroup_id"]  # xxx:
        return not bool(self.errors)


class LoginUserEditForm(Form):
    auth_identifier = fields.TextField(
        label=u"名前", validators=[validators.Length(max=255)])
    auth_secret = fields.TextField(
        label=u"password", validators=[validators.Length(max=255)])

    def object_validate(self, user_qs, loginuser):
        if not self.validate():
            return False
        another = user_qs.filter(
            Member.id != loginuser.id,
            Member.auth_identifier == self.data["auth_identifier"]).first()
        if another:
            self.errors["auth_identifier"] = [u"同じ名前が既に登録されています"]
            return False
        return True
