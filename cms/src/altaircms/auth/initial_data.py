# coding: utf-8
from altaircms.models import DBSession
from altaircms.auth.models import Role, RolePermission, DEFAULT_ROLE, PERMISSIONS, target_objects


def insert_initial_authdata():
    role = Role(id=1, name=DEFAULT_ROLE)
    DBSession.add(role)

    for perm in PERMISSIONS:
        roleperm = RolePermission(role_id=role.id, permission=perm)
        DBSession.add(roleperm)

    i = 2 # administratorが1なので、2以降が通常ロール
    for obj in target_objects:
        for perm in ('viewer', 'editor'):
            role = Role(id=i, name='%s_%s' % (obj, perm))
            DBSession.add(role)

            if perm == 'viewer' or perm == 'editor':
                # read権限つける
                role_perm = RolePermission(role_id=role.id, permission='%s_read' % (obj, ))
                DBSession.add(role_perm)

            if perm == 'editor':
                for p in ('create', 'update', 'delete'):
                    role_perm = RolePermission(role_id=role.id, permission='%s_%s' % (obj, p ))
                    DBSession.add(role_perm)

            i+=1