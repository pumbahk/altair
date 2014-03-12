# -*- coding: utf-8 -*-
"""add column Permission.name_kana OparatorRole.name_kana

Revision ID: 1328638422b3
Revises: 3c93bddaec70
Create Date: 2014-02-28 19:07:25.272840

"""

# revision identifiers, used by Alembic.
revision = '1328638422b3'
down_revision = '182d3dffdf7a'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('OperatorRole', sa.Column('name_kana', sa.Unicode(length=255), nullable=True))
    op.execute(u"UPDATE OperatorRole SET name_kana = 'Altair管理者' WHERE name = 'administrator'")
    op.execute(u"UPDATE OperatorRole SET name_kana = '管理者' WHERE name = 'superuser'")
    op.execute(u"UPDATE OperatorRole SET name_kana = 'オペレーター' WHERE name = 'operator'")
    op.execute(u"UPDATE OperatorRole SET name_kana = 'スーパーオペレーター' WHERE name = 'superoperator'")

def downgrade():
    op.drop_column('OperatorRole', 'name_kana')
