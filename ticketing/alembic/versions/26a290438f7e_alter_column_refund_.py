"""alter column Refund.start_at

Revision ID: 26a290438f7e
Revises: 366d63c6a3d6
Create Date: 2013-09-03 16:18:53.322756

"""

# revision identifiers, used by Alembic.
revision = '26a290438f7e'
down_revision = '366d63c6a3d6'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.alter_column('Refund', 'start_at', nullable=True, type_=sa.DateTime(), existing_type=sa.DateTime(), existing_nullable=False)
    op.alter_column('Refund', 'end_at', nullable=True, type_=sa.DateTime(), existing_type=sa.DateTime(), existing_nullable=False)

def downgrade():
    op.alter_column('Refund', 'start_at', nullable=False, type_=sa.DateTime(), existing_type=sa.DateTime(), existing_nullable=True)
    op.alter_column('Refund', 'end_at', nullable=False, type_=sa.DateTime(), existing_type=sa.DateTime(), existing_nullable=True)
