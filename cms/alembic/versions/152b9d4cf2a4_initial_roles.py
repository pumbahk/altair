"""initial roles

Revision ID: 152b9d4cf2a4
Revises: 368ab65b72b1
Create Date: 2012-05-06 20:40:01.944476

"""

# revision identifiers, used by Alembic.
revision = '152b9d4cf2a4'
down_revision = '368ab65b72b1'

from alembic import op
import sqlalchemy as sa

import sqlahelper
from sqlalchemy.sql.functions import max
from altaircms.auth.models import Role, RolePermission, DEFAULT_ROLE, PERMISSIONS
DBSession = sqlahelper.get_session()

def upgrade():
    
    # administrator
    role = Role(name=DEFAULT_ROLE, permissions=PERMISSIONS)
    DBSession.add(role)

    perms = ["_create", "_read", "_delete", "_update"]
    for target in ['event', 'topic', 'topcontent', 'ticket', 'magazine', 'asset', 'page', 'tag', 'promotion', 'promotion_unit', 'performance', 'layout', 'operator', "hotword"]:
        # viewer
        role = Role(name=target + "_viewer", permissions=[target + "_read"])
        DBSession.add(role)
        # editor
        role = Role(name=target + "_editor", permissions=[(target + perm) for perm in perms])
        DBSession.add(role)
    import transaction
    transaction.commit()

def downgrade():
    RolePermission.query.delete()
    Role.query.delete()
    import transaction
    transaction.commit()
