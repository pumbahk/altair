# -*- coding:utf-8 -*-
import json
import logging
import csv
import itertools
from wtforms import Form
from wtforms import fields
from wtforms import widgets
from wtforms import validators
from collections import namedtuple, OrderedDict

logger = logging.getLogger(__name__)

class MemberShipChoicesForm(Form):
    membership_id = fields.SelectField(
        label=u"Membership", 
        choices=[], 
        coerce=unicode
        )
    
    def configure(self, memberships):
        self.membership_id.choices = [(m.id, m.name) for m in memberships]
        return self


class MemberCSVImportForm(Form):
    csvfile = fields.FileField(label=u"csvファイル")
    encoding = fields.SelectField(label=u"エンコーディング", 
                                  choices=(("cp932", u"windowsのファイル"), ("utf-8", u"UTF-8")))

    def validate(self):
        super(MemberCSVImportForm, self).validate()
        io = self.data["csvfile"].file
        try:
            reader = csv.reader(io, quotechar="'", encoding=self.data["encoding"])
            for membergroup_name, loginname, password in reader:
                pass
        except UnicodeDecodeError as e:
            logger.info("*csv import* %s" % (str(e)))
            self.csvfile.errors = self.errors["csvfile"] = [u"csvファイルが壊れています。あるいは指定しているエンコーディングが異なっているかもしません。"]
        except Exception as e:
            logger.info(e.__class__)
            logger.info("*csv import* %s" % (str(e)))
            self.csvfile.errors = self.errors["csvfile"] = [u"csvファイルが壊れています。"]
        import pdb; pdb.set_trace()
        io.seek(0)
        return not bool(self.errors)

class MemberGroupChoicesForm(Form):
    membergroup_id = fields.SelectField(
        label=u"Membergroup", 
        choices=[], 
        coerce=unicode
        )

    user_id_list = fields.HiddenField(
        label=u"", 
        )
    def validate_user_id_list(form, field):
        field.data = json.loads(field.data)

    def configure(self, membergroups):
        self.membergroup_id.choices = [(m.id, m.name) for m in membergroups]
        return self

    def validate(self):
        super(self.__class__, self).validate()
        if "membergroup_id" in self.errors:
            del self.errors["membergroup_id"] #xxx:
        return not bool(self.errors)

