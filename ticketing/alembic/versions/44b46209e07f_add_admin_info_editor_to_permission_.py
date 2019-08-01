"""add admin_info_editor to permission table

Revision ID: 44b46209e07f
Revises: 52e1704387c5
Create Date: 2019-07-30 16:07:23.765341

"""

# revision identifiers, used by Alembic.
revision = '44b46209e07f'
down_revision = '52e1704387c5'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.execute("INSERT INTO Permission (operator_role_id, category_name, permit) VALUES(1, 'admin_info_editor', 1)")
    op.execute("INSERT INTO Permission (operator_role_id, category_name, permit) VALUES(2, 'admin_info_editor', 1)")


def downgrade():
    op.execute("DELETE FROM Permission WHERE operator_role_id=1 AND category_name='admin_info_editor' AND permit=1")
    op.execute("DELETE FROM Permission WHERE operator_role_id=2 AND category_name='admin_info_editor' AND permit=1")
