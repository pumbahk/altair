# -*- coding:utf-8 -*-

"""setup RT cart

Revision ID: 17984d0ecfd2
Revises: ada129db897
Create Date: 2013-03-22 17:22:03.927687

Add two new columns; auth_type is for determining how to authenticate a comer in the cart and performance_selector is for determining in which way the performance is chosen.
"""

# revision identifiers, used by Alembic.
revision = '17984d0ecfd2'
down_revision = 'ada129db897'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.execute("""UPDATE OrganizationSetting JOIN Organization ON Organization.id = OrganizationSetting.organization_id
SET auth_type = 'rakuten', performance_selector = 'date'
WHERE Organization.short_name = 'RT'
""")

def downgrade():
    # 戻す意味あるんだろうか
    op.execute("""UPDATE OrganizationSetting JOIN Organization ON Organization.id = OrganizationSetting.organization_id
SET auth_type = 'fc_auth', performance_selector = 'matchup'
WHERE Organization.short_name = 'RT'
""")

