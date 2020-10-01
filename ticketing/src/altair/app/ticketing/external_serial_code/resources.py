# -*- coding:utf-8 -*-
from datetime import datetime
from altair.app.ticketing import csvutils

import transaction
from altair.app.ticketing.core.models import Organization
from altair.app.ticketing.operators.models import Operator
from altair.app.ticketing.orders.models import ExternalSerialCodeSetting, ExternalSerialCode
from altair.app.ticketing.resources import TicketingAdminResource
from altair.sqlahelper import get_db_session
from sqlalchemy import desc, or_


class ExternalSerialCodeBase(TicketingAdminResource):

    def __init__(self, request):
        self.session = get_db_session(request, name="slave")
        super(ExternalSerialCodeBase, self).__init__(request)

    @property
    def setting_id(self):
        return self.request.matchdict.get("setting_id", None)

    @property
    def setting(self):
        return self.session.query(ExternalSerialCodeSetting) \
            .filter_by(organization_id=self.organization.id) \
            .filter(ExternalSerialCodeSetting.id == self.setting_id) \
            .first()

    def get_operator(self, operator_id):
        return Operator.query.filter(Operator.id == operator_id).first()

    def get_organization(self, organization_id):
        return Organization.query.filter(Organization.id == organization_id).first()


class ExternalSerialCodeSettingResource(ExternalSerialCodeBase):
    def __init__(self, request):
        super(ExternalSerialCodeSettingResource, self).__init__(request)

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


class ExternalSerialCodeResource(ExternalSerialCodeBase):
    def __init__(self, request):
        super(ExternalSerialCodeResource, self).__init__(request)

    @property
    def code_id(self):
        return self.request.matchdict.get("code_id", None)

    @property
    def master_code(self):
        # アップデート予定のマスタから取得した設定
        return ExternalSerialCode.query \
            .join(ExternalSerialCodeSetting,
                  ExternalSerialCodeSetting.id == ExternalSerialCode.external_serial_code_setting_id) \
            .filter(ExternalSerialCodeSetting.organization_id == self.organization.id) \
            .filter(ExternalSerialCode.id == self.code_id) \
            .first()

    @property
    def master_codes_not_ordered(self):
        # アップデート予定のマスタから取得した設定
        return ExternalSerialCode.query \
            .join(ExternalSerialCodeSetting,
                  ExternalSerialCodeSetting.id == ExternalSerialCode.external_serial_code_setting_id) \
            .filter(ExternalSerialCodeSetting.organization_id == self.organization.id) \
            .filter(ExternalSerialCode.used_at == None) \
            .all()

    def validate_delete_code(self):
        code = self.master_code
        if code.tokens:
            return True
        if code.used_at:
            return True
        return False

    def get_master_codes(self, organization_id, setting_id):
        return ExternalSerialCode.query \
            .join(ExternalSerialCodeSetting,
                  ExternalSerialCodeSetting.id == ExternalSerialCode.external_serial_code_setting_id) \
            .filter(ExternalSerialCodeSetting.id == setting_id) \
            .filter(ExternalSerialCodeSetting.organization_id == organization_id) \
            .order_by(desc(ExternalSerialCode.id)) \
            .all()

    def get_codes(self, search_form):
        query = self.session.query(ExternalSerialCode) \
            .join(ExternalSerialCodeSetting,
                  ExternalSerialCodeSetting.id == ExternalSerialCode.external_serial_code_setting_id) \
            .filter(ExternalSerialCodeSetting.organization_id == self.organization.id) \
            .filter(ExternalSerialCode.external_serial_code_setting_id == self.setting_id) \

        if search_form and search_form.search_word.data:
            query = query.filter(
                or_(
                    ExternalSerialCode.code_1.like(u"%{0}%".format(search_form.search_word.data)),
                    ExternalSerialCode.code_2.like(u"%{0}%".format(search_form.search_word.data))
                )
            )

        query = query.order_by(desc(ExternalSerialCode.id))
        return query.all()

    def delete_code(self):
        self.master_code.deleted_at = datetime.now()
        organization_id = self.organization.id
        operator_id = self.user.id
        transaction.commit()
        self.user = self.get_operator(operator_id)
        self.organization = self.get_organization(organization_id)

    def delete_all_code(self):
        for code in self.master_codes_not_ordered:
            code.deleted_at = datetime.now()
        organization_id = self.organization.id
        operator_id = self.user.id
        transaction.commit()
        self.user = self.get_operator(operator_id)
        self.organization = self.get_organization(organization_id)

    def import_codes(self, setting, form):
        io = form.data["upload_file"].file
        reader = csvutils.reader(
            io, quotechar="'", encoding="shift_jis")

        num = 0
        for code_1_name, code_1, code_2_name, code_2 in reader:
            if num == 0:
                num = num + 1
                continue
            code = ExternalSerialCode()
            code.code_1_name = code_1_name
            code.code_1 = code_1
            code.code_2_name = code_2_name
            code.code_2 = code_2
            code.external_serial_code_setting_id = setting.id
            code.save()

        io.seek(0)
        transaction.commit()

