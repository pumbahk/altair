"""fix-sejfile-enum

Revision ID: 185c98fe4e30
Revises: 4763d4675ab5
Create Date: 2013-07-24 13:32:42.280283

"""

# revision identifiers, used by Alembic.
revision = '185c98fe4e30'
down_revision = '4763d4675ab5'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.alter_column('SejFile', 'notification_type', sa.Enum('51', '61', '92', '94', '95', '96'), existing_type=sa.Enum('94', '51', '61', '92', '94', '95', '96'), existing_nullable=True)

def downgrade():
    # no need to restore the original state
    pass
