"""user_point_account

Revision ID: 35f24964b70c
Revises: 489071e335a
Create Date: 2013-05-09 14:03:46.614800

"""

# revision identifiers, used by Alembic.
revision = '35f24964b70c'
down_revision = '489071e335a'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.alter_column(
        'UserPointAccount', 'point_type_code',
        nullable=False,
        name='type',
        server_default='0',
        existing_type=sa.Integer
        )

def downgrade():
    op.alter_column(
        'UserPointAccount', 'type',
        nullable=True,
        name='point_type_code',
        existing_type=sa.Integer
        )
