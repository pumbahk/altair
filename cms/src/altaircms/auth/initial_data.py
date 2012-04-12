# coding: utf-8
import sqlahelper
from sqlalchemy.sql.functions import max
from altaircms.auth.models import Role, RolePermission, Permission, DEFAULT_ROLE


# 対象オブジェクト
target_objects = ['event', 'topic', 'ticket', 'magazine', 'asset', 'page', 'tag', 'layout', 'operator']
PERMISSIONS = []
for t in target_objects:
    for act in ('create', 'read', 'update', 'delete'):
        PERMISSIONS.append('%s_%s' % (t, act))


def insert_initial_authdata():
    """
    ロールとパーミッションを登録する
    """

    DBSession = sqlahelper.get_session()

    # administrator
    role = Role(id=1, name=DEFAULT_ROLE)
    DBSession.add(role)

    # register all permissions to administrator
    for permission_id, strperm in enumerate(PERMISSIONS, 1):
        permission = Permission(id=permission_id, name=strperm)
        DBSession.add(permission)

    for role_permission_id, permission in enumerate(DBSession.query(Permission).all(), 1):
        roleperm = RolePermission(id=role_permission_id, role_id=1, permission_id=permission.id)
        DBSession.add(roleperm)

    # regsiter roles
    role_id = 2 # 1はadministratorなので2から
    role_permission_id = int(DBSession.query(max(RolePermission.id)).one()[0]) + 1

    for obj in target_objects:
        for strperm in ('viewer', 'editor'):
            role = Role(id=role_id, name='%s_%s' % (obj, strperm))
            DBSession.add(role)
            role_id += 1

            if strperm == 'viewer' or strperm == 'editor':
                # read権限つける
                permission = DBSession.query(Permission).filter_by(name='%s_read' % (obj,)).one()
                role_perm = RolePermission(id=role_permission_id, role_id=role.id, permission_id=permission.id)
                DBSession.add(role_perm)

                role_permission_id += 1

            if strperm == 'editor':
                for p in ('create', 'update', 'delete'):
                    permission = DBSession.query(Permission).filter_by(name='%s_%s' % (obj, p)).one()
                    role_perm = RolePermission(id=role_permission_id, role_id=role.id, permission_id=permission.id)
                    DBSession.add(role_perm)
                    role_permission_id += 1
