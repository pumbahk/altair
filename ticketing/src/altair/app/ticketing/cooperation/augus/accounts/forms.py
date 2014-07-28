# -*- coding: utf-8 -*-
from wtforms import PasswordField
from sqlalchemy.orm.exc import (
    NoResultFound,
    MultipleResultsFound,
    )
from altair.formhelpers import (
    OurForm,
    OurTextField,
    OurSelectField,
    OurIntegerField,
    )
from altair.saannotation import get_annotations_for
from altair.formhelpers import (
    Required,
    Translations
    )
from altair.app.ticketing.core.models import (
    AugusAccount,
    Organization,
    )

_label = lambda field: get_annotations_for(field)['label']


class AugusAccountForm(OurForm):
    def __init__(self, formdata=None, obj=None, prefix='', **kwds):
        self.organization_id = kwds.pop('organization_id', None)
        super(self.__class__, self).__init__(formdata, obj, prefix, **kwds)

        if 'data' in kwds and kwds['data'] is not None:
            d = kwds['data']
            for k in d.__table__.columns:
                if k.name in self:
                    self[k.name].data = getattr(d, k.name)
        try:
            organization = Organization.query.filter(Organization.id==self.organization_id).one()
            self.account_id.choices = [(account.id, account.name) for account in organization.accounts]
        except (NoResultFound, MultipleResultsFound) as err:
            raise

    account_id = OurSelectField(
        label=u'アカウント',
        validators=[Required(u'選択してください')],
        coerce=int,
        )

    code = OurIntegerField(
        label=_label(AugusAccount.code),
        )
    name = OurTextField(
        label=_label(AugusAccount.name),
        )
    host = OurTextField(
        label=_label(AugusAccount.host),
        )
    username = OurTextField(
        label=_label(AugusAccount.username),
        )
    password = PasswordField(
        label=_label(AugusAccount.password),
        )
    send_dir = OurTextField(
        label=_label(AugusAccount.send_dir),
        )
    recv_dir = OurTextField(
        label=_label(AugusAccount.recv_dir),
        )
