# -*- coding: utf-8 -*-

import re

from wtforms import Form, ValidationError
from wtforms import TextField, HiddenField, DateField, PasswordField, SelectMultipleField, BooleanField
from wtforms.validators import Length, Optional, Regexp
from pyramid.security import has_permission, ACLAllowed

from altair.formhelpers import Translations, Required, PHPCompatibleSelectMultipleField, strip_spaces, NFKC, Email
from altair.formhelpers.fields import DateTimeField
from altair.formhelpers.widgets import CheckboxMultipleSelect
from altair.app.ticketing.operators.models import Operator, OperatorAuth, OperatorRole, Permission, ensure_ascii
from altair.app.ticketing.permissions.utils import PermissionCategory
from altair.app.ticketing.models import DBSession


class ReviewAuthorizationForm(Form):
    id = HiddenField(
        label=u'ID',
        validators=[Optional()],
    )
    order_no = HiddenField(
        label=u'予約番号',
        validators=[Optional()],
    )
    review_password = PasswordField(
        label=u'受付確認用パスワード',
        validators=[
            Required(message=u'入力してください'),
            Length(min=8, max=16, message=u'8文字以上16文字以内で入力してください。'),
            Regexp(r'^(?=.*[a-zA-Z])(?=.*[0-9])([A-Za-z0-9]+)$', 0, message=u'半角の英文字と数字を組み合わせてご入力ください。大文字も使用できます。'),
        ]
    )
    email = TextField(
        label=u'メールアドレス',
        validators=[
            Required(message=u'入力してください'),
            Email(),
        ]
    )
