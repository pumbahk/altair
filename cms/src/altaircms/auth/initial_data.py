# coding: utf-8
from altaircms.models import DBSession
from altaircms.auth.models import Role, RolePermission, DEFAULT_ROLE, PERMISSIONS

def insert_initial_authdata():
    role = Role(id=1, name=DEFAULT_ROLE)
    DBSession.add(role)

    for perm in PERMISSIONS:
        roleperm = RolePermission(role_id=role.id, permission=perm)
        DBSession.add(roleperm)
