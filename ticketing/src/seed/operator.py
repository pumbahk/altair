# -*- coding: utf-8 -*-

from seed import DataSet
from ticketing.models import *
from ticketing.models.boxoffice import *
from permission import PermissionData
from datetime import datetime
from client import ClientData

class OperatorRoleData(DataSet):
    class role_admin_admin:
        name = 'Administrator'
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
            PermissionData.page_editor,
            PermissionData.tag_editor,
            PermissionData.layout_viewer,
            PermissionData.layout_editor
        ]
        updated_at = datetime.now()
        created_at = datetime.now()
        status = 1

    class role_super_user:
        name = 'Superuser'
        permissions = [
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
            PermissionData.page_editor,
            PermissionData.tag_editor,
            PermissionData.layout_viewer,
            PermissionData.layout_editor
        ]
        updated_at = datetime.now()
        created_at = datetime.now()
        status = 1

class OperatorData(DataSet):
    class operator_1:
        name = 'Administrator'
        email = 'admin@ticketstar.com'
        client = ClientData.client_1
        updated_at = datetime.now()
        created_at = datetime.now()
        status = 1
        login_id = 'admin'
        password =  md5('admin').hexdigest()
        auth_code = 'auth_code'
        access_token = 'access_token'
        secret_key = 'secret_key'
        roles = [
            OperatorRoleData.role_admin_admin
        ]
    class operator_2:
        name = 'オペレーター2'
        email = 'tes2t@test.com'
        client = ClientData.client_1
        updated_at = datetime.now()
        created_at = datetime.now()
        status = 1
        login_id = 'testtest'
        password =  md5('test').hexdigest()
        auth_code = 'auth_code'
        access_token = 'access_token'
        secret_key = 'secret_key'
        roles = [
            OperatorRoleData.role_super_user
        ]
