# coding: utf-8
# alembicに移動して削除

import sqlahelper
from altaircms.auth.models import Role, DEFAULT_ROLE, PERMISSIONS


# 対象オブジェクト
# target_objects = ['event', 'topic', 'ticket', 'magazine', 'asset', 'page', 'tag', 'layout', 'operator']
# PERMISSIONS = []
# for t in target_objects:
#     for act in ('create', 'read', 'update', 'delete'):
#         PERMISSIONS.append('%s_%s' % (t, act))
# 

def insert_initial_authdata():
    """
    ロールとパーミッションを登録する
    """

    DBSession = sqlahelper.get_session()

    # administrator
    role = Role(name=DEFAULT_ROLE, permissions=PERMISSIONS)
    DBSession.add(role)

    perms = ["_create", "_read", "_delete", "_update"]
    for target in ['event', 'topic', 'ticket', 'magazine', 'asset', 'page', 'tag', 'layout', 'operator']:
        # viewer
        role = Role(name=target + "_viewer", permissions=[target + "_read"])
        # editor
        role = Role(name=target + "_editor", permissions=[(target + perm) for perm in perms])
