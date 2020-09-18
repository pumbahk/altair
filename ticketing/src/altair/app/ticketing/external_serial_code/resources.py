# -*- coding:utf-8 -*-
from datetime import datetime

import transaction
from altair.app.ticketing.core.models import Organization
from altair.app.ticketing.operators.models import Operator
from altair.app.ticketing.orders.models import ExternalSerialCodeSetting
from altair.app.ticketing.resources import TicketingAdminResource
from altair.sqlahelper import get_db_session
from sqlalchemy import desc


class ExternalSerialCodeBase(TicketingAdminResource):

    def __init__(self, request):
        self.session = get_db_session(request, name="slave")
        super(ExternalSerialCodeBase, self).__init__(request)


class ExternalSerialCodeSettingResource(ExternalSerialCodeBase):
    def __init__(self, request):
        super(ExternalSerialCodeSettingResource, self).__init__(request)

    @property
    def setting_id(self):
        return self.request.matchdict.get("setting_id", None)

    @property
    def setting(self):
        return self.session.query(ExternalSerialCodeSetting) \
            .filter_by(organization_id=self.organization.id) \
            .filter(ExternalSerialCodeSetting.id == self.setting_id) \
            .first()

    @property
    def master_setting(self):
        # アップデート予定のマスタから取得した設定
        return ExternalSerialCodeSetting.query \
            .filter_by(organization_id=self.organization.id) \
            .filter(ExternalSerialCodeSetting.id == self.setting_id) \
            .first()

    def delete_setting(self):
        self.master_setting.deleted_at = datetime.now()
        organization_id = self.organization.id
        operator_id = self.user.id
        transaction.commit()
        self.user = self.get_operator(operator_id)
        self.organization = self.get_organization(organization_id)

    def get_settings(self, search_form):
        query = self.session.query(ExternalSerialCodeSetting) \
            .filter_by(organization_id=self.organization.id)

        if search_form and search_form.name.data:
            query = query.filter(ExternalSerialCodeSetting.name.like(u"%{0}%".format(search_form.name.data)))

        query = query.order_by(desc(ExternalSerialCodeSetting.created_at))
        return query.all()

    def get_master_settings(self):
        return ExternalSerialCodeSetting.query \
            .filter_by(organization_id=self.organization.id) \
            .order_by(desc(ExternalSerialCodeSetting.created_at)) \
            .all()

    def get_operator(self, operator_id):
        return Operator.query.filter(Operator.id==operator_id).first()

    def get_organization(self, organization_id):
        return Organization.query.filter(Organization.id==organization_id).first()
