#-*- coding: utf-8 -*-
from sqlalchemy.orm.exc import (
    NoResultFound,
    MultipleResultsFound,
    )

from wtforms import (
    Form,
    FileField,
    TextField,
    IntegerField,
    PasswordField,
    )


from altair.formhelpers import (
    Required,
    Translations,
    OurSelectField,
    OurTextField
    )
from altair.app.ticketing.core.models import Organization, AugusPerformance


class AugusVenueUploadForm(Form):
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
            self.augus_account_id.choices = [
                (account.augus_account.id, account.augus_account.name)
                for account in organization.accounts
                if account.augus_account
                ]
        except (NoResultFound, MultipleResultsFound) as err:
            raise

    augus_account_id = OurSelectField(
        label=u'アカウント',
        validators=[Required(u'選択してください')],
        coerce=int,
        )

    augus_venue_file = FileField(
        label=u'CSVファイル',
        validators=[],
        )


class AugusVenueDownloadForm(Form):
    def __init__(self, formdata=None, obj=None, prefix='', **kwds):
        self.organization_id = kwds.pop('organization_id', None)
        super(self.__class__, self).__init__(formdata, obj, prefix, **kwds)

        try:
            organization = Organization.query.filter(Organization.id==self.organization_id).one()
            augus_performances
            self.augus_account_id.choices = [
                (account.augus_account.id, account.augus_account.name)
                for account in organization.accounts
                if account.augus_account
                ]
        except (NoResultFound, MultipleResultsFound) as err:
            raise

    augus_account_id = OurSelectField(
        label=u'アカウント',
        validators=[Required(u'選択してください')],
        coerce=int,
        )


class AugusPerformanceSearchForm(Form):
    search_text = OurTextField(
        label=u'検索文字列',
        validators=[],
    )
