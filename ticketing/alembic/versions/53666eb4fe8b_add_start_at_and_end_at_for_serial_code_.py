"""add start_at and end_at for serial code setting table

Revision ID: 53666eb4fe8b
Revises: 1f34e17bbbf5
Create Date: 2019-10-25 17:18:24.024570

"""

# revision identifiers, used by Alembic.
revision = '53666eb4fe8b'
down_revision = '1f34e17bbbf5'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.execute('''ALTER TABLE ExternalSerialCodeSetting ADD start_at TIMESTAMP NOT NULL AFTER description;''')
    op.execute('''ALTER TABLE ExternalSerialCodeSetting ADD end_at TIMESTAMP AFTER start_at;''')


def downgrade():
    op.drop_column('ExternalSerialCodeSetting', 'start_at')
    op.drop_column('ExternalSerialCodeSetting', 'end_at')
