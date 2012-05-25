# -*- coding: utf-8 -*-

from ticketing.seed import DataSet
from datetime import datetime
from hashlib import md5

from permission import PermissionData
from organization import OrganizationData

class OperatorRoleData(DataSet):
    class role_admin_admin:
        name = 'administrator'
        permissions = [
            PermissionData.administrator,
            PermissionData.asset_editor,
            PermissionData.event_viewer,
            PermissionData.event_editor,
            PermissionData.topic_viewer,
            PermissionData.ticket_editor,
            PermissionData.magazine_viewer,
            PermissionData.magazine_editor,
            PermissionData.asset_viewer,
            PermissionData.asset_editor,
            PermissionData.page_viewer,
            PermissionData.page_editor,
            PermissionData.tag_editor,
            PermissionData.layout_viewer,
            PermissionData.layout_editor
        ]
    class role_super_user:
        name = 'Superuser'
        permissions = [
            PermissionData.asset_editor_1,
            PermissionData.event_viewer_1,
            PermissionData.event_editor_1,
            PermissionData.topic_viewer_1,
            PermissionData.ticket_editor_1,
            PermissionData.magazine_viewer_1,
            PermissionData.magazine_editor_1,
            PermissionData.asset_viewer_1,
            PermissionData.asset_editor_1,
            PermissionData.page_viewer_1,
            PermissionData.page_editor_1,
            PermissionData.tag_editor_1,
            PermissionData.layout_viewer_1,
            PermissionData.layout_editor_1
        ]

class OperatorData(DataSet):
    class operator_1:
        name = 'Administrator'
        email = 'admin@ticketstar.com'
        organization = OrganizationData.organization_0
        roles = [
            OperatorRoleData.role_admin_admin
        ]
    class operator_2:
        name = 'オペレーター2'
        email = 'tes2t@test.com'
        organization = OrganizationData.organization_0
        roles = [
            OperatorRoleData.role_super_user
        ]

class OperatorAuthData(DataSet):
    class operator_auth_1:
        operator = OperatorData.operator_1
        login_id = 'admin'
        password =  md5('admin').hexdigest()
        auth_code = 'auth_code'
        access_token = 'access_token'
        secret_key = 'secret_key'

    class operator_auth_2:
        operator = OperatorData.operator_2
        login_id = 'testtest'
        password =  md5('test').hexdigest()
        auth_code = 'auth_code'
        access_token = 'access_token'
        secret_key = 'secret_key'

