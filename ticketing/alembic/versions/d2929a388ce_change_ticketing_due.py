"""change_ticketing_due_datetime

Revision ID: d2929a388ce
Revises: 2655d4d39145
Create Date: 2012-09-08 22:55:00.736515

"""

# revision identifiers, used by Alembic.
revision = 'd2929a388ce'
down_revision = '2655d4d39145'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger

def upgrade():
    op.alter_column('SejNotification', 'ticketing_due_datetime',
        name='ticketing_due_at',
        existing_type=sa.DateTime(),
        existing_server_default=text('NULL'),
        existing_nullable=True)
    op.alter_column('SejNotification', 'ticketing_due_datetime_new',
        name='ticketing_due_at_new',
        existing_type=sa.DateTime(),
        existing_server_default=text('NULL'),
        existing_nullable=True)

def downgrade():
    op.alter_column('SejNotification', 'ticketing_due_at',
        name='ticketing_due_datetime',
        existing_type=sa.DateTime(),
        existing_server_default=text('NULL'),
        existing_nullable=True)
    op.alter_column('SejNotification', 'ticketing_due_at_new',
        name='ticketing_due_datetime_new',
        existing_type=sa.DateTime(),
        existing_server_default=text('NULL'),
        existing_nullable=True)
